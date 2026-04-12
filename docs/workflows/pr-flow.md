# PR Flow

Flow for creating commits and pull requests in the hybrid model.

## Sequence

1. Codex validates the diff.
2. Codex confirms changed files are in scope.
3. Codex confirms that a validation artifact exists for the task.
4. Claude Code may use `/hybrid-commit`.
5. Codex verifies git state and commit quality.
6. Claude Code may use `/hybrid-pr`.
7. Codex verifies PR title, summary, risks, and test plan.

## Guardrail

Do not run `/commit` or `/pr` before validation is complete.
Do not run `/hybrid-commit` or `/hybrid-pr` without a plan reference and validation context.
These are Claude-side commands; Codex may orchestrate them, but does not execute them as native commands.
