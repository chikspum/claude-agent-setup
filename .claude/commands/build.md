# /build

Build the repository through the repo-local build surface. Report full vs degraded execution honestly.

Steps:
1. Prefer the repo-local entrypoint: `bash scripts/build.sh`
2. If you need language-specific detail, map the build outcome back to:
   - Python dependency/bootstrap step
   - `cd tools/go && go build ./...`
   - `cd tools/cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel`
3. If the repo script reports degraded mode, say so explicitly and list the missing primary tools.
4. If a step fails, report the failing area and stop only after capturing enough information for Codex to validate the failure cleanly.
5. If the build is tied to a tracked task, mention the plan path and any run-log or validation-artifact path Codex should update.

## Output Format

```markdown
## Context
- <plan path or n/a>
- <run log path or n/a>

## Repo Command
- `bash scripts/build.sh`: PASS / FAIL / PASS (degraded mode)

| Area | Command | Result | Notes |
|------|---------|--------|-------|
| Python | `...` | PASS / FAIL / SKIPPED | ... |
| Go | `...` | PASS / FAIL / SKIPPED | ... |
| C++ | `...` | PASS / FAIL / SKIPPED | ... |

## Environment Gaps
- <missing primary tools or n/a>
```
