# /fix $ARGUMENTS

Bug fixer — finds the root cause of an error or bug description, applies a minimal targeted fix, and verifies it.

`$ARGUMENTS` should be an error message, stack trace, or plain-language bug description.

## Routing

Before starting, identify which directory contains the broken code:

- `tools/python/` or `*.py` → delegate to **python-agent**
- `tools/go/` or `*.go` → delegate to **go-agent**
- `tools/cpp/` or `*.cpp` / `*.h` → delegate to **cpp-agent**
- Spans multiple languages → **orchestrator** coordinates, delegates per-language fixes separately
- Config, agents, CLAUDE.md → handle directly (no delegation)

Pass the full error message and file path to the sub-agent. Do not start the steps below until the correct agent is identified.

---

## Steps
1. **Parse the input.** Extract:
   - File names or module names mentioned in the error
   - Function or method names
   - Line numbers if present
   - Key error terms (e.g., `nil pointer`, `index out of range`, `KeyError`)

2. **Locate relevant code.** Search the codebase:
   - Start with any file/line references in the error
   - Search for the function or symbol names mentioned
   - Check callers if the error originates in a utility or shared module
   - Read enough context (±20 lines around the suspected location) to understand the logic

3. **Identify the root cause.** Explain in one or two sentences what the actual bug is — not just what the error message says, but *why* it happens. Common patterns to look for:
   - Nil/null dereference before a guard check
   - Off-by-one in a loop or slice index
   - Unchecked error return being used
   - Wrong type assumption or missing type assertion
   - Race condition or missing mutex
   - Incorrect default value or uninitialized variable

4. **Apply a minimal fix.**
   - Change only the code that is actually broken
   - Do not refactor surrounding code, rename variables, or clean up unrelated issues
   - If there's a defensive fix (nil check, bounds check) and a proper fix (fix the logic), prefer the proper fix and explain the tradeoff

5. **Run tests to verify.**
   - Python: `pytest` (or the nearest `test_*.py`)
   - Go: `go test ./...` from the module root
   - C++: `cmake --build build && ctest --test-dir build`
   - If tests don't exist for the affected code, note that and suggest adding one
   - **If tests fail after the fix, do NOT report as complete.** Iterate on the fix or report a partial result with a clear explanation of what still fails.

6. **Report what changed and why:**
   ```
   Root cause: <one sentence>
   Fix: <what was changed, referencing file:line>
   Verified: <test command and result>
   ```

Keep the fix surgical. If the bug reveals a deeper design issue, mention it in a follow-up note but do not fix it in the same change.
