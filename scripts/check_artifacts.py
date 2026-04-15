#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATIONS_DIR = ROOT / "artifacts" / "validations"
RUNS_DIR = ROOT / "artifacts" / "runs"

RUN_REQUIRED_PATTERNS = {
    "run_id": ["- run_id:"],
    "date": ["- date:"],
    "operator": ["- operator:"],
    "task_id": ["- task_id:", "- task id:"],
    "plan_file": ["- plan_file:", "- plan file:"],
    "goal": ["- goal:"],
    "scope": ["- scope:"],
    "status": ["- status:"],
    "summary": ["- summary:"],
}

VALIDATION_REQUIRED_PATTERNS = {
    "task_id": ["- task_id:", "- task id:"],
    "plan_file": ["- plan_file:", "- plan file:"],
    "claude_run_summary": ["- claude_run_summary:", "- claude run summary:"],
    "scope_summary": ["- scope_summary:", "- scope summary:"],
    "changed_files_section": ["## Changed Files"],
    "checks_run_section": ["## Checks Run"],
    "skipped_checks_section": ["## Skipped Checks"],
    "acceptance_decision_section": ["## Acceptance Decision"],
}


def iter_markdown_files(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.name not in {"README.md", "TEMPLATE.md", ".gitkeep"}
    )


def missing_patterns(path: Path, required: dict[str, list[str]]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [name for name, patterns in required.items() if not any(pattern in text for pattern in patterns)]


def main() -> int:
    errors: list[str] = []

    for path in iter_markdown_files(VALIDATIONS_DIR):
        missing = missing_patterns(path, VALIDATION_REQUIRED_PATTERNS)
        if missing:
            errors.append(f"{path.relative_to(ROOT)} missing validation keys: {', '.join(missing)}")

    for path in iter_markdown_files(RUNS_DIR):
        missing = missing_patterns(path, RUN_REQUIRED_PATTERNS)
        if missing:
            errors.append(f"{path.relative_to(ROOT)} missing run-log keys: {', '.join(missing)}")

    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1

    print("artifact structure checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
