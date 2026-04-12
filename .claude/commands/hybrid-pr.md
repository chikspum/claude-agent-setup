# /hybrid-pr

PR helper for the hybrid workflow.

Only use this after Codex has validated the branch scope and commit set.

## Preconditions

- Codex has accepted the diff
- commits accurately represent the validated work
- test/check status is known
- a validation artifact exists and can be cited in the PR body
- the work maps to a plan file or an explicitly tracked task id

If any precondition is unclear, stop and report what Codex still needs to validate.

## Steps

1. Identify the plan file, validation artifact, and any run log relevant to the branch.
2. Run `/pr`.
3. Keep the PR summary grounded in validated behavior only.
4. In the test plan, distinguish:
   - checks that passed
   - checks that were skipped
   - checks blocked by missing tools or environment setup
5. Reference the validation artifact in the summary or testing notes when useful.
6. If `gh` is unavailable or unauthenticated, provide the PR draft content for Codex to inspect.

## Output Format

```markdown
## PR Status
- READY / BLOCKED / CREATED

## Artifact Context
- <plan path>
- <validation artifact path>
- <run log path or n/a>

## Title
- <title>

## Summary Notes
- <what the PR says>

## Validation Notes For Codex
- <checks passed>
- <checks skipped>
- <environment gaps>
```
