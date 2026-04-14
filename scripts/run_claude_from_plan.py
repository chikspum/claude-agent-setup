#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = 120
DEBUG_ARTIFACT_DIR = ROOT / "artifacts" / "debug" / "claude-bridge"

RunOutcome = Literal["success", "partial_success", "failure"]


@dataclass
class ValidationCheck:
    command: str
    result: str
    notes: str


@dataclass
class BridgeInspection:
    outcome: RunOutcome
    changed_files: list[str]
    in_scope_files: list[str]
    out_of_scope_files: list[str]
    meaningful_diff: bool
    repo_broken: bool
    validation_checks: list[ValidationCheck] = field(default_factory=list)
    follow_up_recommended: bool = False
    follow_up_actions: list[str] = field(default_factory=list)
    summary: str = ""
    changed_files_summary: str = "none"
    diff_stats: str = "none"
    debug_artifact_path: str | None = None


@dataclass
class FileState:
    exists: bool
    is_file: bool
    digest: str | None
    size: int


def extract_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    collected: list[str] = []
    capture = False

    for line in lines:
        if line.startswith("## "):
            name = line[3:].strip()
            if name == heading:
                capture = True
                continue
            if capture:
                break
        if capture:
            collected.append(line)

    return collected


def extract_metadata_value(lines: list[str], key: str) -> str:
    patterns = [f"- {key}:", f"- {key.replace('_', ' ')}:"]
    for line in lines:
        stripped = line.strip()
        for pattern in patterns:
            if stripped.startswith(pattern):
                return stripped.split(":", 1)[1].strip()
    return ""


def extract_scoped_list(lines: list[str], label: str) -> list[str]:
    results: list[str] = []
    capture = False

    for line in lines:
        stripped = line.strip()
        if stripped.lower() == f"- {label}:".lower():
            capture = True
            continue
        if capture:
            if stripped.startswith("- ") and not line.startswith("  "):
                break
            if stripped.startswith("- "):
                results.append(stripped[2:].strip())
            elif stripped:
                results.append(stripped)

    return [item for item in results if item]


def extract_bullets(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    current: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if item.endswith(":"):
                current = item[:-1].strip()
                continue
            if current:
                bullets.append(f"{current}: {item}")
                current = None
            else:
                bullets.append(item)
        elif current and stripped.startswith(("* ", "- ")):
            bullets.append(f"{current}: {stripped[2:].strip()}")
            current = None
        elif current and stripped:
            bullets.append(f"{current}: {stripped}")
            current = None

    return bullets


def build_brief(plan_path: Path) -> tuple[str, str]:
    text = plan_path.read_text(encoding="utf-8")
    metadata = extract_section(text, "Metadata")
    problem = "\n".join(line for line in extract_section(text, "Problem") if line.strip()).strip()
    scope = extract_section(text, "Scope")
    validation = extract_section(text, "Validation Strategy")
    work_items = extract_section(text, "Claude Work Items")

    task_id = extract_metadata_value(metadata, "task_id") or plan_path.stem
    required_changes = extract_scoped_list(scope, "files expected to change")
    forbidden_changes = extract_scoped_list(scope, "files that must not change")
    stable_interfaces = extract_scoped_list(scope, "public interfaces that must remain stable")
    validation_items = extract_bullets(validation)
    claude_items = extract_bullets(work_items)

    constraint_lines = [
        "do not modify unrelated files",
        "do not change public interfaces unless explicitly requested",
    ]
    constraint_lines.extend(stable_interfaces)

    verification_lines = validation_items or [
        "follow the plan validation strategy and report skipped checks explicitly"
    ]

    work_scope = claude_items or ["execute the current bounded work item from the referenced plan"]

    brief = (
        "\n".join(
            [
                f"You are working in {ROOT}.",
                "",
                f"Plan path: {plan_path}",
                f"Task id: {task_id}",
                "",
                "Goal:",
                f"- {problem or 'Execute the bounded work defined in the plan.'}",
                "",
                "Required changes:",
                *[f"- {item}" for item in required_changes],
                *[f"- {item}" for item in work_scope if item not in required_changes],
                "",
                "Forbidden changes:",
                *[f"- {item}" for item in forbidden_changes],
                "",
                "Constraints:",
                *[f"- {item}" for item in constraint_lines],
                "",
                "Use repository commands when helpful:",
                "- /handoff semantics are already represented by this plan",
                "- /test for repo-native checks",
                "- /commit only after Codex validation",
                "- /pr only after Codex validation",
                "",
                "Verification:",
                *[f"- {item}" for item in verification_lines],
                "",
                "Final response:",
                "- files changed",
                "- tests and checks run",
                "- skipped checks and why",
                "- residual issues",
                "- suggested run log path if the task was material",
            ]
        ).strip()
        + "\n"
    )

    return task_id, brief


def extract_plan_scope(plan_path: Path) -> tuple[str, list[str], list[str], list[str]]:
    text = plan_path.read_text(encoding="utf-8")
    metadata = extract_section(text, "Metadata")
    scope = extract_section(text, "Scope")
    validation = extract_section(text, "Validation Strategy")
    task_id = extract_metadata_value(metadata, "task_id") or plan_path.stem
    required_changes = extract_scoped_list(scope, "files expected to change")
    forbidden_changes = extract_scoped_list(scope, "files that must not change")
    validation_items = extract_bullets(validation)
    return task_id, required_changes, forbidden_changes, validation_items


def normalize_scope_path(item: str) -> str | None:
    candidate = item.split(":", 1)[0].strip().strip("`")
    if not candidate or " " in candidate and "/" not in candidate:
        return None
    candidate_path = Path(candidate)
    if candidate_path.is_absolute():
        try:
            return str(candidate_path.resolve().relative_to(ROOT))
        except ValueError:
            return None
    if candidate.startswith(".") and not candidate.startswith("./"):
        return candidate
    return str(candidate_path)


def allowed_scope_paths(required_changes: list[str]) -> set[str]:
    allowed: set[str] = set()
    for item in required_changes:
        normalized = normalize_scope_path(item)
        if normalized:
            allowed.add(normalized)
    return allowed


def capture_repo_snapshot(root: Path) -> dict[str, FileState]:
    snapshot: dict[str, FileState] = {}
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        try:
            relative = str(path.relative_to(root))
        except ValueError:
            continue
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            snapshot[relative] = FileState(
                exists=True, is_file=True, digest=digest, size=path.stat().st_size
            )
        else:
            snapshot[relative] = FileState(exists=True, is_file=False, digest=None, size=0)
    return snapshot


def detect_changed_files(before: dict[str, FileState], after: dict[str, FileState]) -> list[str]:
    changed: list[str] = []
    all_paths = set(before) | set(after)
    for relative in sorted(all_paths):
        left = before.get(relative)
        right = after.get(relative)
        if left is None or right is None:
            changed.append(relative)
            continue
        if left.exists != right.exists or left.is_file != right.is_file:
            changed.append(relative)
            continue
        if left.is_file and (left.digest != right.digest or left.size != right.size):
            changed.append(relative)
    return changed


def summarize_changed_files(changed_files: list[str]) -> str:
    if not changed_files:
        return "none"
    return ", ".join(changed_files)


def git_diff_stats(paths: list[str]) -> str:
    if not paths:
        return "none"
    command = ["git", "-C", str(ROOT), "diff", "--stat", "--", *paths]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    text = completed.stdout.strip()
    return text or "none"


def run_validation_checks(validation_commands: list[str]) -> tuple[list[ValidationCheck], bool]:
    checks: list[ValidationCheck] = []
    repo_broken = False
    for command in validation_commands:
        completed = subprocess.run(
            ["bash", "-lc", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        output_lines = []
        if completed.stdout.strip():
            output_lines.append(completed.stdout.strip().splitlines()[-1])
        if completed.stderr.strip():
            output_lines.append(completed.stderr.strip().splitlines()[-1])
        note = " | ".join(output_lines) if output_lines else "completed"
        result = "PASS" if completed.returncode == 0 else "FAIL"
        if completed.returncode != 0:
            repo_broken = True
        checks.append(ValidationCheck(command=command, result=result, notes=note))
    return checks, repo_broken


def is_meaningful_change(changed_files: list[str], diff_stats: str) -> bool:
    if not changed_files:
        return False
    if diff_stats != "none":
        return True
    return any(not path.endswith((".tmp", ".log")) for path in changed_files)


def suggest_follow_up_actions(changed_files: list[str]) -> list[str]:
    suggestions: list[str] = []
    lower_paths = [path.lower() for path in changed_files]
    if any("test_" in path or path.endswith("_test.py") for path in lower_paths):
        suggestions.append("only rerun the relevant validation and confirm the existing tests pass")
    if any(path.endswith("pyproject.toml") or path.endswith("go.mod") for path in lower_paths):
        suggestions.append(
            "only finish packaging or module registration for the existing implementation"
        )
    code_paths = [
        path
        for path in changed_files
        if path.endswith((".py", ".go", ".cpp", ".h", ".md")) and "test_" not in path
    ]
    if code_paths:
        suggestions.append(
            f"only add tests or validation around the already-created file: {code_paths[0]}"
        )
    return suggestions[:3]


def inspect_abnormal_run(
    *,
    task_id: str,
    required_changes: list[str],
    validation_commands: list[str],
    before_snapshot: dict[str, FileState],
    stdout: str,
    stderr: str,
    timeout_seconds: int,
    process_exit_code: int | None,
    timed_out: bool,
) -> BridgeInspection:
    after_snapshot = capture_repo_snapshot(ROOT)
    changed_files = detect_changed_files(before_snapshot, after_snapshot)
    allowed = allowed_scope_paths(required_changes)
    in_scope_files = [path for path in changed_files if not allowed or path in allowed]
    out_of_scope_files = [path for path in changed_files if allowed and path not in allowed]
    diff_stats = git_diff_stats(changed_files)
    meaningful_diff = is_meaningful_change(changed_files, diff_stats)

    validation_checks: list[ValidationCheck] = []
    repo_broken = False
    if meaningful_diff and not out_of_scope_files and validation_commands:
        validation_checks, repo_broken = run_validation_checks(validation_commands)

    follow_up_actions: list[str] = []
    follow_up_recommended = False

    if not meaningful_diff:
        outcome: RunOutcome = "failure"
        summary = "No meaningful repository diff was produced before the abnormal Claude exit."
    elif out_of_scope_files:
        outcome = "failure"
        repo_broken = True
        summary = (
            "Claude produced out-of-scope edits; the run is not recoverable as partial success."
        )
    else:
        outcome = "partial_success"
        if validation_checks and all(check.result == "PASS" for check in validation_checks):
            summary = (
                "Claude timed out after making meaningful in-scope changes; post-run checks passed."
            )
        else:
            follow_up_recommended = True
            follow_up_actions = suggest_follow_up_actions(changed_files)
            summary = (
                "Claude timed out after making meaningful in-scope changes; "
                "the result is salvageable but still needs a narrow "
                "follow-up or acceptance review."
            )

    inspection = BridgeInspection(
        outcome=outcome,
        changed_files=changed_files,
        in_scope_files=in_scope_files,
        out_of_scope_files=out_of_scope_files,
        meaningful_diff=meaningful_diff,
        repo_broken=repo_broken,
        validation_checks=validation_checks,
        follow_up_recommended=follow_up_recommended,
        follow_up_actions=follow_up_actions,
        summary=summary,
        changed_files_summary=summarize_changed_files(changed_files),
        diff_stats=diff_stats,
    )
    inspection.debug_artifact_path = str(
        write_debug_artifact(
            task_id=task_id,
            timeout_seconds=timeout_seconds,
            process_exit_code=process_exit_code,
            timed_out=timed_out,
            stdout=stdout,
            stderr=stderr,
            inspection=inspection,
        )
    )
    return inspection


def write_debug_artifact(
    *,
    task_id: str,
    timeout_seconds: int,
    process_exit_code: int | None,
    timed_out: bool,
    stdout: str,
    stderr: str,
    inspection: BridgeInspection,
) -> Path:
    DEBUG_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = DEBUG_ARTIFACT_DIR / f"{timestamp}-{task_id}.json"
    payload = {
        "task_id": task_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "process_exit_code": process_exit_code,
        "stdout_tail": stdout.strip().splitlines()[-20:],
        "stderr_tail": stderr.strip().splitlines()[-20:],
        "changed_files_summary": inspection.changed_files_summary,
        "changed_files": inspection.changed_files,
        "in_scope_files": inspection.in_scope_files,
        "out_of_scope_files": inspection.out_of_scope_files,
        "meaningful_diff": inspection.meaningful_diff,
        "diff_stats": inspection.diff_stats,
        "repo_broken": inspection.repo_broken,
        "validation_checks": [asdict(check) for check in inspection.validation_checks],
        "follow_up_recommended": inspection.follow_up_recommended,
        "follow_up_actions": inspection.follow_up_actions,
        "outcome": inspection.outcome,
        "summary": inspection.summary,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def render_claude_output(stdout: str, output_format: str) -> str:
    if output_format != "json":
        return stdout

    stripped = stdout.strip()
    if not stripped:
        return ""

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return stdout

    if isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, str) and result.strip():
            return result.rstrip() + "\n"

    return stdout


def run_claude(
    plan_path: Path,
    permission_mode: str,
    claude_bin: str,
    timeout_seconds: int,
    output_format: str,
    no_session_persistence: bool,
) -> int:
    task_id, brief = build_brief(plan_path)
    _, required_changes, _, validation_commands = extract_plan_scope(plan_path)
    before_snapshot = capture_repo_snapshot(ROOT)
    command = [
        claude_bin,
        "-p",
        "--output-format",
        output_format,
        "--permission-mode",
        permission_mode,
        "--add-dir",
        str(ROOT),
    ]
    if no_session_persistence:
        command.append("--no-session-persistence")

    try:
        completed = subprocess.run(
            command,
            input=brief,
            text=True,
            cwd=ROOT,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError:
        sys.stderr.write(
            f"claude runner not found: {claude_bin}\n"
            "Install Claude Code CLI or pass --claude-bin with the correct executable path.\n"
        )
        return 127
    except subprocess.TimeoutExpired as exc:
        inspection = inspect_abnormal_run(
            task_id=task_id,
            required_changes=required_changes,
            validation_commands=validation_commands,
            before_snapshot=before_snapshot,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            timeout_seconds=timeout_seconds,
            process_exit_code=None,
            timed_out=True,
        )
        sys.stdout.write("## Handoff Runner\n")
        sys.stdout.write(f"- plan: {plan_path}\n")
        sys.stdout.write(f"- task_id: {task_id}\n")
        sys.stdout.write(f"- permission_mode: {permission_mode}\n")
        sys.stdout.write(f"- command: {' '.join(command)}\n")
        sys.stdout.write(f"- timeout_seconds: {timeout_seconds}\n\n")

        partial_stdout = exc.stdout or ""
        partial_stderr = exc.stderr or ""
        rendered = render_claude_output(partial_stdout, output_format)
        if rendered:
            sys.stdout.write(rendered)
            if not rendered.endswith("\n"):
                sys.stdout.write("\n")

        if partial_stderr:
            sys.stderr.write(partial_stderr)
            if not partial_stderr.endswith("\n"):
                sys.stderr.write("\n")

        sys.stdout.write("## Bridge Inspection\n")
        sys.stdout.write(f"- outcome: {inspection.outcome}\n")
        sys.stdout.write(f"- changed_files: {inspection.changed_files_summary}\n")
        sys.stdout.write(f"- diff_stats: {inspection.diff_stats}\n")
        sys.stdout.write(f"- debug_artifact: {inspection.debug_artifact_path}\n")
        sys.stdout.write(f"- summary: {inspection.summary}\n")
        if inspection.follow_up_actions:
            sys.stdout.write("- follow_up_actions:\n")
            for item in inspection.follow_up_actions:
                sys.stdout.write(f"  - {item}\n")
        if inspection.validation_checks:
            sys.stdout.write("- validation_checks:\n")
            for check in inspection.validation_checks:
                sys.stdout.write(f"  - {check.command}: {check.result} ({check.notes})\n")
        sys.stdout.write("\n")

        if inspection.outcome == "partial_success":
            return 75
        return 124

    sys.stdout.write("## Handoff Runner\n")
    sys.stdout.write(f"- plan: {plan_path}\n")
    sys.stdout.write(f"- task_id: {task_id}\n")
    sys.stdout.write(f"- permission_mode: {permission_mode}\n")
    sys.stdout.write(f"- timeout_seconds: {timeout_seconds}\n")
    sys.stdout.write(f"- command: {' '.join(command)}\n\n")

    rendered_stdout = render_claude_output(completed.stdout, output_format)

    if rendered_stdout:
        sys.stdout.write(rendered_stdout)
        if not rendered_stdout.endswith("\n"):
            sys.stdout.write("\n")

    if completed.stderr:
        sys.stderr.write(completed.stderr)
        if not completed.stderr.endswith("\n"):
            sys.stderr.write("\n")

    if completed.returncode != 0:
        inspection = inspect_abnormal_run(
            task_id=task_id,
            required_changes=required_changes,
            validation_commands=validation_commands,
            before_snapshot=before_snapshot,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timeout_seconds=timeout_seconds,
            process_exit_code=completed.returncode,
            timed_out=False,
        )
        sys.stdout.write("## Bridge Inspection\n")
        sys.stdout.write(f"- outcome: {inspection.outcome}\n")
        sys.stdout.write(f"- changed_files: {inspection.changed_files_summary}\n")
        sys.stdout.write(f"- diff_stats: {inspection.diff_stats}\n")
        sys.stdout.write(f"- debug_artifact: {inspection.debug_artifact_path}\n")
        sys.stdout.write(f"- summary: {inspection.summary}\n")
        if inspection.follow_up_actions:
            sys.stdout.write("- follow_up_actions:\n")
            for item in inspection.follow_up_actions:
                sys.stdout.write(f"  - {item}\n")
        if inspection.validation_checks:
            sys.stdout.write("- validation_checks:\n")
            for check in inspection.validation_checks:
                sys.stdout.write(f"  - {check.command}: {check.result} ({check.notes})\n")
        sys.stdout.write("\n")
        if inspection.outcome == "partial_success":
            return 75

    after_snapshot = capture_repo_snapshot(ROOT)
    changed_files = detect_changed_files(before_snapshot, after_snapshot)
    allowed = allowed_scope_paths(required_changes)
    diff_stats = git_diff_stats(changed_files)
    success_inspection = BridgeInspection(
        outcome="success",
        changed_files=changed_files,
        in_scope_files=[path for path in changed_files if not allowed or path in allowed],
        out_of_scope_files=[path for path in changed_files if allowed and path not in allowed],
        meaningful_diff=is_meaningful_change(changed_files, diff_stats),
        repo_broken=False,
        summary="Claude returned a clean final response.",
        changed_files_summary=summarize_changed_files(changed_files),
        diff_stats=diff_stats,
    )
    sys.stdout.write("## Bridge Inspection\n")
    sys.stdout.write(f"- outcome: {success_inspection.outcome}\n")
    sys.stdout.write(f"- changed_files: {success_inspection.changed_files_summary}\n")
    sys.stdout.write(f"- diff_stats: {success_inspection.diff_stats}\n")
    sys.stdout.write(f"- summary: {success_inspection.summary}\n\n")

    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Claude Code against a repository plan.")
    parser.add_argument("plan", help="Path to the plan file to execute.")
    parser.add_argument(
        "--permission-mode",
        default="acceptEdits",
        help="Claude permission mode. Defaults to acceptEdits.",
    )
    parser.add_argument(
        "--claude-bin",
        default="claude",
        help="Claude CLI executable. Defaults to 'claude'.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "Maximum Claude runtime before the bridge fails cleanly. "
            f"Defaults to {DEFAULT_TIMEOUT_SECONDS}."
        ),
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="json",
        help="Claude print output format. Defaults to json for machine-readable bridge output.",
    )
    parser.add_argument(
        "--session-persistence",
        choices=["enabled", "disabled"],
        default="disabled",
        help=(
            "Whether Claude session persistence should stay enabled for bridge runs. "
            "Defaults to disabled."
        ),
    )
    parser.add_argument(
        "--print-brief",
        action="store_true",
        help="Print the generated brief instead of running Claude.",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path
    plan_path = plan_path.resolve()

    if not plan_path.exists():
        sys.stderr.write(f"plan file not found: {plan_path}\n")
        return 1

    _, brief = build_brief(plan_path)
    if args.print_brief:
        sys.stdout.write(brief)
        return 0

    return run_claude(
        plan_path,
        args.permission_mode,
        args.claude_bin,
        args.timeout_seconds,
        args.output_format,
        args.session_persistence == "disabled",
    )


if __name__ == "__main__":
    raise SystemExit(main())
