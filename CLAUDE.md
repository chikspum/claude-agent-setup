# claude-agent-setup

Claude Code operating context for this repository.

This file is intentionally short. Use `docs/` for durable detail and `AGENTS.md` as the shared map.

## Read Order

1. [AGENTS.md](/home/ubuntu/claude-agent-setup/AGENTS.md)
2. [docs/index.md](/home/ubuntu/claude-agent-setup/docs/index.md)
3. [docs/architecture/boundaries.md](/home/ubuntu/claude-agent-setup/docs/architecture/boundaries.md)
4. [docs/workflows/hybrid-execution.md](/home/ubuntu/claude-agent-setup/docs/workflows/hybrid-execution.md)
5. [docs/workflows/validation.md](/home/ubuntu/claude-agent-setup/docs/workflows/validation.md)

## Role

Claude Code is the scoped executor.

Default expectations:

- work inside the files and constraints provided by Codex
- use repo-native commands and scripts instead of inventing ad hoc flows
- report changed files, checks run, skipped checks, and residual issues
- do not treat your own output as accepted until Codex validates it

## Primary Entry Points

Repository commands:

- `bash scripts/build.sh`
- `bash scripts/test.sh`
- `bash scripts/lint.sh`

If `make` is installed, `make build`, `make test`, and `make lint` are strict wrappers around the same scripts.

Primary Claude slash commands:

- `/build`
- `/doc`
- `/review`
- `/test`
- `/status`
- `/commit`
- `/pr`
- `/init`
- `/handoff <plan-file>`
- `/hybrid-doc <target>`
- `/hybrid-test`
- `/hybrid-fix <issue>`
- `/hybrid-commit`
- `/hybrid-pr`

See [docs/references/command-reference.md](/home/ubuntu/claude-agent-setup/docs/references/command-reference.md).
These are Claude-side runtime affordances that Codex may orchestrate, not Codex-native commands.

## Boundaries

- keep changes inside the requested scope
- respect ownership in `agents/` and `config/agents.yaml`
- ask before changing public APIs, deleting files, or widening scope
- prefer updating `docs/` over expanding root files

## Required Output

For non-trivial work, respond with:

- files changed
- commands run
- skipped or degraded checks
- open risks or blockers

If a command relied on fallback tooling, say that explicitly.
