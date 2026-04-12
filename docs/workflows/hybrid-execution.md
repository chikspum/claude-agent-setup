# Hybrid Execution

Standard operating workflow for `Codex -> Claude Code`.

## Goal

Make delegation predictable, reviewable, and cheap to validate.

## Supported Production Mode

The supported production-default mode for this repository is:

`Codex -> plan -> Claude Code execution -> Codex validation`

Codex may perform trivial direct work when delegation is clearly slower than the change itself, but direct Codex execution is the exception path, not the primary operating model.

## Flow

1. Codex reads the target files locally.
2. Codex defines the exact outcome, scope, and validation commands.
3. Codex writes or updates a plan artifact for non-trivial work.
4. Codex writes a constrained Claude execution brief.
5. Claude Code executes the scoped task.
6. Claude Code or Codex records a run log if the execution is material.
7. Codex reviews `git diff`.
8. Codex reruns tests, lint, and build checks as needed.
9. Codex accepts, patches minor defects, or sends a narrower follow-up brief.

## Handoff Contract

Every Claude execution brief should contain:

- repo path
- goal
- required changes
- forbidden changes
- constraints
- verification commands
- expected final response format

Use [references/claude-brief-template.md](/home/ubuntu/claude-agent-setup/docs/references/claude-brief-template.md).
For CLI-specific invocation guidance, see [references/claude-cli-handoff.md](/home/ubuntu/claude-agent-setup/docs/references/claude-cli-handoff.md).
For production runtime and restriction guidance, see [references/codex-runtime-profiles.md](/home/ubuntu/claude-agent-setup/docs/references/codex-runtime-profiles.md) and [references/restrictions.md](/home/ubuntu/claude-agent-setup/docs/references/restrictions.md).

For non-trivial work, also carry:

- a plan file under `docs/plans/active/`
- a validation artifact under `artifacts/validations/` once Codex accepts the result
- a run log under `artifacts/runs/` when execution details would help future sessions

## Delegation Rules

Delegate to Claude Code when work is:

- localized
- repetitive
- scaffold-oriented
- documentation-oriented
- straightforward to verify

Keep work in Codex when work is:

- architectural
- ambiguous
- high-risk
- cross-cutting in a way that depends on subtle judgment

## Acceptance Rule

Claude Code output is never final until Codex validates it locally.
