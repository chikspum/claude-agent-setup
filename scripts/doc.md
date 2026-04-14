# Bridge And Scripts

## About
`scripts/` contains the executable bridge and verification entrypoints used by Codex and Claude Code inside this repository.

## Read This When
- You are changing Claude bridge execution behavior.
- You are debugging timeout, partial-success, slicing, or abnormal-run handling.
- You are changing repo-local build, test, lint, docs-drift, or metrics checks.

## Related Docs
- `../doc.md`
- `../docs/doc.md`
- `../tools/doc.md`
- `../config/doc.md`

## Key Files
- `run_claude_from_plan.py` - core plan-driven Claude bridge runner.
- `delegate_to_claude.py` - generates a bounded plan and invokes the bridge.
- `run_claude_handoff.sh` - shell wrapper for bridge execution.
- `build.sh`, `test.sh`, `lint.sh` - repo-local verification entrypoints.
- `check_artifacts.py`, `check_docs_drift.py`, `generate_metrics_summary.py` - policy and metrics automation.
- `check_toolchain.sh` - strict toolchain gate used by `make doctor`.

## Invariants
- Bridge execution must stay bounded by plan scope and explicit validation rules.
- Abnormal runs must remain observable through normalized summaries and debug artifacts.
- Recovery should prefer narrow follow-up slices or micro-probes, not blind broad retries.
- Repo-local scripts are the canonical verification surface; wrappers should not invent parallel behavior that disagrees with them.

## Workflow
1. Start with the bridge runner if the bug affects Claude execution or classification.
2. Read the delegate runner if the issue starts from task shaping or temporary plan generation.
3. Follow into docs and tests before changing recovery semantics or validation policy.
4. Validate with focused tests first, then `py_compile`, `ruff`, and broader repo checks only if the change warrants it.

## Verification
- Focused bridge change: `uv run --extra dev pytest -q test_claude_bridge_runner.py`
- Python syntax: `python3 -m py_compile scripts/run_claude_from_plan.py scripts/delegate_to_claude.py`
- Python lint: `uv run --extra dev ruff check scripts/run_claude_from_plan.py scripts/delegate_to_claude.py tools/python/test_claude_bridge_runner.py`
- Repo gate: `bash scripts/build.sh`, `bash scripts/test.sh`, `bash scripts/lint.sh`, or `make verify`

## Body
`run_claude_from_plan.py` is the highest-impact script in this directory. It parses the plan, derives the Claude brief, enforces timeout and abnormal-run handling, classifies `success` or `partial_success` or `failure`, and writes debug artifacts when recovery analysis is needed.

`delegate_to_claude.py` sits one layer above the bridge. It turns a direct Codex goal into a bounded plan, invokes the same bridge runner, and can draft run-log or validation artifacts for later Codex review.

The remaining shell and policy scripts form the repo-level verification surface. They matter because other docs, plans, and CI workflows assume these entrypoints are the stable operational contract.
