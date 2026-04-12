# Production Gate

Minimum release gate for this repository as an internal-team hybrid-agent workspace.

## Required Conditions

- docs and command surface agree on the supported operating model
- Codex runtime profile guidance exists
- restriction policy exists and is mirrored by runtime enforcement where needed
- at least one delegated docs-only task has completed with run log and validation artifact
- at least one delegated code-edit task has completed with run log and validation artifact
- build, test, and lint entrypoints are documented honestly, including degraded-mode behavior
- machine-readable metrics summary exists and matches the recorded artifacts

## Acceptance Record

A repository state should not be treated as production-ready unless the release gate is reviewed alongside:

- the current scorecard
- the latest run logs
- the latest validation artifacts

## Verification

- regenerate the machine summary with `python3 scripts/generate_metrics_summary.py`
- check for drift with `python3 scripts/generate_metrics_summary.py --check` or `make metrics-check`
