# /test

Run the repository test surface through the repo-local script first, then break out language detail if needed.

Steps:
1. Prefer the repo-local entrypoint: `bash scripts/test.sh`
2. If you need language-specific detail, map the outcome back to:
   - `cd tools/python && pytest -v`
   - `cd tools/go && go test ./... -v`
   - `cd tools/cpp && ctest --test-dir build --output-on-failure`
3. Report `PASS (degraded mode)` when the repo script succeeds via fallback checks instead of full primary-tool validation.
4. If any tests fail, list the failing test names or failing command blocks and the error output.
5. If the run is tied to a tracked task, mention the plan path and any run-log or validation-artifact path Codex should update.

At the end, print:

## Context
- <plan path or n/a>
- <run log path or n/a>

## Repo Command
- `bash scripts/test.sh`: PASS / FAIL / PASS (degraded mode)

| Language | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Python   | ...   | ...    | ...    |
| Go       | ...   | ...    | ...    |
| C++      | ...   | ...    | ...    |

Also state any missing tools that prevented full validation.
