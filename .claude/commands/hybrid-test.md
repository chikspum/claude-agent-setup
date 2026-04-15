# /hybrid-test

Hybrid validation-oriented test workflow for Claude Code under Codex review.

## Goal

Run the repository's test flow and report missing tooling honestly.

## Steps

1. Prefer the repo-local entrypoint: `bash scripts/test.sh`.
2. If you need language-specific detail, break out the same underlying checks:
   - `cd tools/python && pytest -v`
   - `cd tools/go && go test ./... -v`
   - `cd tools/cpp && ctest --test-dir build --output-on-failure`
3. If a test directory or build artifact is missing, report it explicitly.
4. If a required tool is missing from the environment, report `SKIPPED (missing tool)` or `PASS (degraded mode)` accurately rather than implying full validation.
5. If the task is tracked by a plan, mention the plan path and the run-log or validation-artifact path Codex should update.
6. Do not collapse all results into one sentence; keep repo-level and language-specific outcomes separate so Codex can validate them.

## Output Format

```markdown
## Context
- <plan path or n/a>
- <run log path or n/a>

## Repo Command
- `bash scripts/test.sh`: PASS / FAIL / SKIPPED

| Area | Command | Result | Notes |
|------|---------|--------|-------|
| Python | `...` | PASS / FAIL / SKIPPED | ... |
| Go | `...` | PASS / FAIL / SKIPPED | ... |
| C++ | `...` | PASS / FAIL / SKIPPED | ... |

## Failures
- <failing test or missing prerequisite>
```
