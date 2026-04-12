# Command Reference

Hybrid workflow command map.

## Primary Claude Code Commands

These commands belong to Claude Code runtime and match the primary command list in `CLAUDE.md`.
Codex may instruct Claude Code to use them, but Codex does not execute them as native built-ins.

- `/build`: run the repo-local build workflow
- `/doc`: generate or refresh documentation
- `/review`: secondary review pass
- `/test`: run repository test workflow
- `/status`: show repo health across git, build, test, lint, and TODOs
- `/commit`: commit after Codex validation
- `/pr`: prepare PR after Codex validation
- `/init`: scaffold new components using repo patterns
- `/handoff <plan-file>`: execute a bounded plan artifact
- `/hybrid-doc <target>`: run documentation work in a Codex-reviewable format
- `/hybrid-test`: run tests with explicit missing-tool reporting
- `/hybrid-fix <issue>`: apply the smallest bounded fix
- `/hybrid-commit`: guarded commit flow for validated diffs
- `/hybrid-pr`: guarded PR flow for validated branches

## Codex Shell Checks

- `bash scripts/build.sh`
- `bash scripts/test.sh`
- `bash scripts/lint.sh`
- `bash scripts/run_claude_handoff.sh docs/plans/active/<plan-file>.md`
- `python3 scripts/delegate_to_claude.py --goal "..." --change "path: exact change"`
- `python3 scripts/delegate_to_claude.py --goal "..." --write-run-log-draft`
- `python3 scripts/delegate_to_claude.py --goal "..." --write-validation-draft`
- `make handoff PLAN=docs/plans/active/<plan-file>.md`
- `make delegate GOAL="..."`
- `make delegate GOAL="..." RUN_LOG_DRAFT=1`
- `make delegate GOAL="..." RUN_LOG_DRAFT=1 VALIDATION_DRAFT=1`
- `git status --short`
- `git diff --stat`
- `git diff`
- `make build` if `make` is available and strict validation is desired
- `make test` if `make` is available and strict validation is desired
- `make lint` if `make` is available and strict validation is desired

## Validation System

- machine-readable policy: [config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml)
- artifact template: [artifacts/validations/TEMPLATE.md](/home/ubuntu/claude-agent-setup/artifacts/validations/TEMPLATE.md)
- machine-readable summary: [artifacts/metrics/summary.json](/home/ubuntu/claude-agent-setup/artifacts/metrics/summary.json)
- artifact structure check: `python3 scripts/check_artifacts.py`
- docs and policy drift check: `python3 scripts/check_docs_drift.py`
- summary check: `python3 scripts/generate_metrics_summary.py --check`
