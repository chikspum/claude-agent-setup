# /handoff $ARGUMENTS

Execute a bounded task from a repository plan artifact instead of a free-form prompt.

`$ARGUMENTS` should be a path to a plan file, usually under `docs/plans/active/`.

## Goal

Turn a written Codex plan into a disciplined Claude execution pass.

## Steps

1. Read the plan file in full.
2. Extract:
   - problem
   - scope
   - milestones
   - Claude work items
   - validation strategy
   - exit criteria
3. Restate the execution scope before editing:
   - files expected to change
   - files that must not change
   - public interfaces that must remain stable
4. Derive the task id from the plan metadata if present.
5. Execute only the current bounded work item(s) from the plan.
6. Run the plan's listed verification commands that are feasible in the current environment.
7. Use `config/validation.yaml` to choose the closest validation profile for the work you performed.
8. If a required tool is missing, report that explicitly.
9. If the task is material, prepare enough detail for a run log under `artifacts/runs/`.
10. Do not mark the task complete based on your own judgment alone; report what you changed and what you verified so Codex can validate.
11. If the task is non-trivial, include enough information for Codex to record or update a validation artifact under `artifacts/validations/`.

## Output Format

```markdown
## Plan
- <plan path>
- <task id>

## Scope Applied
- <files changed or intended to change>
- <files intentionally not touched>

## Work Completed
- <completed item>

## Checks Run
- <command>: PASS / FAIL / SKIPPED

## Artifact Notes
- run log suggested: <path or n/a>
- validation artifact: <path or n/a>

## Residual Issues
- <missing tools, blockers, or follow-up items>
```
