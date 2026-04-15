#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def extract_bullets_under_heading(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    capture = False
    current_level = None

    for line in lines:
        if line.startswith("#"):
            normalized = line.lstrip("#").strip()
            if normalized == heading:
                capture = True
                current_level = len(line) - len(line.lstrip("#"))
                continue
            if capture and len(line) - len(line.lstrip("#")) <= current_level:
                break
        if capture and line.startswith("- "):
            bullets.append(line[2:].strip())

    return bullets


def extract_bullets_after_label(text: str, label: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    capture = False

    for line in lines:
        if line.strip() == label:
            capture = True
            continue
        if capture and line.startswith("See "):
            break
        if capture and line.startswith("- "):
            bullets.append(line[2:].strip())

    return bullets


def extract_command_names(items: list[str]) -> list[str]:
    commands: list[str] = []
    for item in items:
        match = re.search(r"`(/[^`]+)`", item)
        if match:
            commands.append(match.group(1))
    return commands


def assert_command_surface_aligned(errors: list[str]) -> None:
    claude_commands = extract_command_names(
        extract_bullets_after_label(read_text("CLAUDE.md"), "Primary Claude slash commands:")
    )
    reference_commands = extract_command_names(
        extract_bullets_under_heading(
            read_text("docs/references/command-reference.md"),
            "Primary Claude Code Commands",
        )
    )
    if claude_commands != reference_commands:
        errors.append(
            "CLAUDE.md primary command list does not match docs/references/command-reference.md"
        )


def assert_restrictions_aligned(errors: list[str]) -> None:
    restrictions = read_text("docs/references/restrictions.md")
    settings = json.loads(read_text(".claude/settings.json"))
    deny_rules = settings["permissions"]["deny"]

    checks = {
        "secrets/": any("secret" in rule.lower() for rule in deny_rules),
        ".ssh/": any(".ssh" in rule for rule in deny_rules),
        ".env": any(".env" in rule for rule in deny_rules),
        "*.pem": any(".pem" in rule for rule in deny_rules),
        "*.key": any(".key" in rule for rule in deny_rules),
        "git reset --hard": any("git reset --hard" in rule for rule in deny_rules),
        "ssh": any("ssh" in rule.lower() for rule in deny_rules),
    }

    for item in extract_bullets_under_heading(restrictions, "Baseline Forbidden Paths"):
        raw = item.strip("`")
        if raw in checks and not checks[raw]:
            errors.append(f"restriction baseline path {raw} is not mirrored in .claude/settings.json")

    for item in extract_bullets_under_heading(restrictions, "Baseline Forbidden Commands"):
        raw = item.strip("`")
        if raw in checks and not checks[raw]:
            errors.append(
                f"restriction baseline command {raw} is not mirrored in .claude/settings.json"
            )


def assert_docs_index_links(errors: list[str]) -> None:
    docs_index = read_text("docs/index.md")
    required_refs = [
        "references/command-reference.md",
        "references/restrictions.md",
        "references/production-gate.md",
    ]
    for ref in required_refs:
        if ref not in docs_index:
            errors.append(f"docs/index.md is missing required reference link: {ref}")


def main() -> int:
    errors: list[str] = []
    assert_command_surface_aligned(errors)
    assert_restrictions_aligned(errors)
    assert_docs_index_links(errors)

    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1

    print("documentation drift checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
