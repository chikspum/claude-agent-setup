# /hybrid-fix $ARGUMENTS

Bounded bug-fix workflow for Claude Code in the Codex-managed hybrid loop.

`$ARGUMENTS` should describe a concrete bug, failing command, or target defect.

## Goal

Apply the smallest plausible fix that Codex can validate quickly.

## Steps

1. Restate the bug in one paragraph.
2. Identify the smallest file set likely involved.
3. Read those files fully before editing.
4. Apply the minimum code or documentation changes needed to address the root cause.
5. Run only the most relevant verification commands for the changed area.
6. If the issue turns out to be broader than the initial scope, stop and say so instead of expanding the patch opportunistically.
7. If the fix is part of a tracked task, mention the plan path and validation artifact path.
8. Report exactly what was changed and what remains uncertain.

## Output Format

```markdown
## Issue
- <bug summary>
- <plan path if applicable>

## Root Cause
- <what was wrong>

## Files Changed
- <path>

## Checks Run
- <command>: PASS / FAIL / SKIPPED

## Artifact Notes
- <validation artifact path or n/a>
- <run log path or n/a>

## Remaining Risk
- <edge case, blocker, or reason to split follow-up work>
```
