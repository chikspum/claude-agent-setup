# /refactor $ARGUMENTS

Refactor the specified file or module ($ARGUMENTS) for improved quality.

**Rules:**
- Do NOT change external behavior or API contracts
- Do NOT add new features
- Run all tests before AND after refactoring to confirm nothing breaks

**Checklist:**
1. Read the target code and its tests
2. Identify issues:
   - Duplicated code → extract shared logic
   - Long functions (>40 lines) → split into composable parts
   - Deep nesting (>3 levels) → early returns, guard clauses
   - Unclear names → rename to reflect intent
   - Dead code → remove
3. Apply changes incrementally, running tests after each change
4. **Verify scope:** run `git diff --name-only` and confirm (a) no files outside the target were modified, (b) the diff size is proportional to the task — if the diff is more than 2× what you expected, stop and reconsider
5. Show a summary of what changed and why

**Output:**
```
## Changes
- [file:line] description of change and reason

## Tests
- Before: X passed
- After:  X passed

## Risk assessment: LOW / MEDIUM
```
