#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = 120


def extract_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    collected: list[str] = []
    capture = False
    level = 0

    for line in lines:
        if line.startswith("## "):
            name = line[3:].strip()
            if name == heading:
                capture = True
                level = 2
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

    verification_lines = validation_items or ["follow the plan validation strategy and report skipped checks explicitly"]

    work_scope = claude_items or ["execute the current bounded work item from the referenced plan"]

    brief = "\n".join(
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
    ).strip() + "\n"

    return task_id, brief


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

        sys.stderr.write(
            "claude bridge timed out before Claude returned a final response; "
            "inspect git diff for partial edits and retry with a narrower scope or a higher timeout.\n"
        )
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
        help=f"Maximum Claude runtime before the bridge fails cleanly. Defaults to {DEFAULT_TIMEOUT_SECONDS}.",
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
        help="Whether Claude session persistence should stay enabled for bridge runs. Defaults to disabled.",
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
