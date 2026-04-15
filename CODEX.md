# CODEX.md

Codex operating context for `claude-agent-setup`.

This file is a policy entrypoint, not the full workflow manual.

## Read Order

1. [AGENTS.md](/home/ubuntu/claude-agent-setup/AGENTS.md)
2. [docs/index.md](/home/ubuntu/claude-agent-setup/docs/index.md)
3. [docs/workflows/hybrid-execution.md](/home/ubuntu/claude-agent-setup/docs/workflows/hybrid-execution.md)
4. [docs/workflows/validation.md](/home/ubuntu/claude-agent-setup/docs/workflows/validation.md)
5. [docs/architecture/toolchain.md](/home/ubuntu/claude-agent-setup/docs/architecture/toolchain.md)

## Role

Codex is the controller and validator.
Claude Code is a bounded execution worker.

This repository is designed for `Codex -> Claude Code`, not for Codex acting as the primary in-repo implementer by default.

Codex owns:

- task intake and decomposition
- plan files for non-trivial work
- acceptance criteria and allowed scope
- local diff review
- final validation and user-facing status

Claude Code may execute work quickly, but it does not decide that work is complete.
Claude-side slash commands are executed by Claude Code, not by Codex directly.

## Default Workflow

1. Inspect the repository locally first.
2. Create or update a plan artifact for non-trivial tasks.
3. Delegate execution-oriented work to Claude Code unless direct Codex work is clearly cheaper and lower-risk.
4. Write a constrained Claude brief when delegating.
5. Review resulting diffs locally.
6. Run the relevant build, test, lint, and doc checks.
7. Accept, patch, or re-scope.

Use [docs/references/claude-brief-template.md](/home/ubuntu/claude-agent-setup/docs/references/claude-brief-template.md) and [docs/references/codex-validation-checklist.md](/home/ubuntu/claude-agent-setup/docs/references/codex-validation-checklist.md).

## Command Surface

Codex may read `.claude/commands/*` and decide when Claude Code should use them.
Codex does not natively execute Claude slash commands itself.

Primary repo-local entrypoints:

- `bash scripts/build.sh`
- `bash scripts/test.sh`
- `bash scripts/lint.sh`

If `make` is available, `make build`, `make test`, and `make lint` run the same flows in strict mode.

Validation policy remains defined by [config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml).

## Non-Negotiables

- do not delegate ambiguous or high-risk work without narrowing scope first
- do not blur the runtime boundary between Codex and Claude Code
- do not present Claude claims without local verification
- do not let root docs become a second system of record
- do not run `git commit` or `git push` unless the user explicitly asks for it in the current conversation
- if tooling is missing, report the gap explicitly in the plan or validation artifact
