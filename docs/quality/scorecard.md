# Quality Scorecard

Use this file to track hybrid-agent workflow quality over time.

## Suggested Metrics

- delegation success rate
- percent of Claude diffs accepted without rework
- median time from brief to validated result
- percent of tasks blocked by environment issues
- percent of tasks requiring Codex direct patching
- recurring failure modes

## Current Snapshot

| Date | Completed Plans | Logged Runs | Validation Artifacts | Environment-Blocked Runs | Notes |
|------|-----------------|-------------|----------------------|--------------------------|-------|
| 2026-04-08 | 1 | 1 | 1 | 1 | initial baseline after phase 5 and 6 rollout |
| 2026-04-09 | 2 | 2 | 2 | 2 | first real tracked task completed; validation surfaced and fixed a fallback test race |
| 2026-04-09 | 3 | 3 | 3 | 3 | first real Codex -> Claude handoff completed after a blocked permission-mode probe |
| 2026-04-09 | 4 | 4 | 4 | 3 | first delegated code-edit task completed and locally verified with pytest |
| 2026-04-12 | 5 | 5 | 5 | 3 | production operating mode, runtime-policy split, and machine-readable metrics summary added |

## Logging Rule

- every completed non-trivial task should have a validation artifact
- every material execution attempt should have a run log
- scorecard rows should summarize completed runs, not proposed work

## Review Cadence

Update this scorecard weekly or after notable workflow failures.

## Machine Summary

The machine-readable companion summary lives at [artifacts/metrics/summary.json](/home/ubuntu/claude-agent-setup/artifacts/metrics/summary.json).
