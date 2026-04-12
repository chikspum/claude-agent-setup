# AGENTS.md

Short index for agent-facing guidance in `claude-agent-setup`.

This file is a map, not the full source of truth.

## Read Order

For Codex agents:

1. [CODEX.md](/home/ubuntu/claude-agent-setup/CODEX.md)
2. [docs/index.md](/home/ubuntu/claude-agent-setup/docs/index.md)
3. [docs/workflows/hybrid-execution.md](/home/ubuntu/claude-agent-setup/docs/workflows/hybrid-execution.md)
4. [docs/workflows/validation.md](/home/ubuntu/claude-agent-setup/docs/workflows/validation.md)

Operating model:

- Codex plans, delegates, validates, and accepts
- Claude Code executes bounded in-repo work and Claude slash commands

For Claude Code:

1. [CLAUDE.md](/home/ubuntu/claude-agent-setup/CLAUDE.md)
2. `.claude/commands/`
3. [docs/index.md](/home/ubuntu/claude-agent-setup/docs/index.md)

## Source Of Truth

Use root files only as entrypoints:

- [CODEX.md](/home/ubuntu/claude-agent-setup/CODEX.md): Codex operating model
- [CLAUDE.md](/home/ubuntu/claude-agent-setup/CLAUDE.md): Claude Code operating model
- [DOC.md](/home/ubuntu/claude-agent-setup/DOC.md): root documentation map
- [HYBRID_AGENT_PLAN.md](/home/ubuntu/claude-agent-setup/HYBRID_AGENT_PLAN.md): strategy and roadmap

Use `docs/` for durable details:

- [docs/architecture/index.md](/home/ubuntu/claude-agent-setup/docs/architecture/index.md): repo boundaries and extension patterns
- [docs/workflows/hybrid-execution.md](/home/ubuntu/claude-agent-setup/docs/workflows/hybrid-execution.md): Codex to Claude handoff flow
- [docs/workflows/validation.md](/home/ubuntu/claude-agent-setup/docs/workflows/validation.md): validation and acceptance rules
- [docs/references/claude-brief-template.md](/home/ubuntu/claude-agent-setup/docs/references/claude-brief-template.md): standard Claude execution brief
- [docs/references/codex-validation-checklist.md](/home/ubuntu/claude-agent-setup/docs/references/codex-validation-checklist.md): standard Codex review checklist
- [docs/plans/active/TEMPLATE.md](/home/ubuntu/claude-agent-setup/docs/plans/active/TEMPLATE.md): plan template for non-trivial work

## Rules

- Keep this file short.
- Do not duplicate long procedural detail here.
- When adding new persistent workflow guidance, put it under `docs/` and link it from this file.
