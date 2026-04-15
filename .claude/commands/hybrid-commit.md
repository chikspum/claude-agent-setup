# /hybrid-commit

Commit helper for the hybrid workflow.

Only use this after Codex has validated the diff.

## Preconditions

- Codex has already reviewed `git diff`
- required checks have passed or been explicitly waived
- there is no unresolved scope drift
- a validation artifact exists for the task
- the task still maps to an active or completed plan file

If any precondition is not clearly true, stop and say that Codex validation is still required.

## Steps

1. Identify the plan file and validation artifact that justify the commit.
2. Run `/commit`.
3. When proposing the commit message, optimize for validated intent, not file inventory.
4. If staged content includes work outside the validated scope, stop and report it instead of committing.
5. Mention the validation artifact and any run log that should be referenced in the commit summary or follow-up notes.

## Output Format

```markdown
## Commit Status
- READY / BLOCKED / COMMITTED

## Artifact Context
- <plan path>
- <validation artifact path>
- <run log path or n/a>

## Reason
- <why it is ready or blocked>

## Proposed Commit
- <commit subject>
- <optional commit body summary>
```
