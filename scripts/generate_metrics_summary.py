#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "artifacts" / "metrics" / "summary.json"


def list_artifact_files(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.name not in {"README.md", "TEMPLATE.md", ".gitkeep"}
    )


def extract_primary_commands(path: Path) -> list[str]:
    commands = []
    pattern = re.compile(r"- `(/[^`]+)`")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line)
        if match:
            commands.append(match.group(1))
    return commands


def extract_environment_note(text: str, labels: list[str]) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        for label in labels:
            prefix = f"- {label}:"
            if stripped.lower().startswith(prefix.lower()):
                return stripped.split(":", 1)[1].strip().lower()
    return "none"


def is_none_like(value: str) -> bool:
    return value == "none" or value.startswith("none ")


def run_has_environment_blocker(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    degraded_paths = extract_environment_note(
        text, ["degraded_paths_used", "degraded paths used"]
    )
    return not is_none_like(degraded_paths)


def build_summary() -> dict:
    completed_plans = list_artifact_files(ROOT / "docs" / "plans" / "completed")
    run_logs = list_artifact_files(ROOT / "artifacts" / "runs")
    validations = list_artifact_files(ROOT / "artifacts" / "validations")

    claude_doc = ROOT / "CLAUDE.md"
    command_reference = ROOT / "docs" / "references" / "command-reference.md"

    summary = {
        "schema_version": "metrics_summary/v1",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "production_defaults": {
            "target": "internal_team",
            "operating_mode": "codex_orchestrates_claude",
            "claude_edit_permission_mode": "acceptEdits",
            "restriction_enforcement": "runtime_plus_policy",
        },
        "artifact_counts": {
            "completed_plans": len(completed_plans),
            "run_logs": len(run_logs),
            "validation_artifacts": len(validations),
            "environment_blocked_runs": sum(
                1 for path in run_logs if run_has_environment_blocker(path)
            ),
        },
        "release_gate": {
            "docs_and_command_surface_aligned": (
                extract_primary_commands(claude_doc)
                == extract_primary_commands(command_reference)
            ),
            "runtime_profile_guidance_present": (
                ROOT / "docs" / "references" / "codex-runtime-profiles.md"
            ).exists(),
            "restriction_policy_present": (
                ROOT / "docs" / "references" / "restrictions.md"
            ).exists()
            and (ROOT / ".claude" / "settings.json").exists(),
            "delegated_docs_task_verified": all(
                (
                    ROOT / "docs" / "plans" / "completed" / "2026-04-09-claude-handoff-smoke.md",
                    ROOT
                    / "artifacts"
                    / "runs"
                    / "2026-04-09-claude-handoff-smoke-run-01.md",
                    ROOT
                    / "artifacts"
                    / "validations"
                    / "2026-04-09-claude-handoff-smoke.md",
                )
            ),
            "delegated_code_task_verified": all(
                (
                    ROOT / "docs" / "plans" / "completed" / "2026-04-09-python-reverse-skill.md",
                    ROOT
                    / "artifacts"
                    / "runs"
                    / "2026-04-09-python-reverse-skill-run-01.md",
                    ROOT
                    / "artifacts"
                    / "validations"
                    / "2026-04-09-python-reverse-skill.md",
                )
            ),
            "machine_readable_summary_present": OUTPUT_PATH.exists(),
            "production_prep_completed": all(
                (
                    ROOT / "docs" / "plans" / "completed" / "2026-04-12-production-prep.md",
                    ROOT
                    / "artifacts"
                    / "runs"
                    / "2026-04-12-production-prep-run-01.md",
                    ROOT
                    / "artifacts"
                    / "validations"
                    / "2026-04-12-production-prep.md",
                )
            ),
        },
        "verified_examples": {
            "docs_only_task": "2026-04-09-claude-handoff-smoke",
            "code_edit_task": "2026-04-09-python-reverse-skill",
        },
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the checked-in summary does not match the generated content.",
    )
    args = parser.parse_args()

    summary = build_summary()
    rendered = json.dumps(summary, indent=2, sort_keys=False) + "\n"

    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != rendered:
            sys.stderr.write(
                "artifacts/metrics/summary.json is out of date; run "
                "`python3 scripts/generate_metrics_summary.py`\n"
            )
            return 1
        return 0

    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
