# claude-agent-setup Documentation Map

`DOC.md` is a root entrypoint, not the full system of record.

Use this file to orient quickly, then move into `docs/` for durable detail.

## Start Here

- [AGENTS.md](/home/ubuntu/claude-agent-setup/AGENTS.md): short read-order map for Codex and Claude Code
- [CODEX.md](/home/ubuntu/claude-agent-setup/CODEX.md): Codex operating model
- [CLAUDE.md](/home/ubuntu/claude-agent-setup/CLAUDE.md): Claude Code operating model
- [codex-claude-code-doc.md](/home/ubuntu/claude-agent-setup/codex-claude-code-doc.md): machine-readable hybrid operating model
- [docs/index.md](/home/ubuntu/claude-agent-setup/docs/index.md): detailed repository docs index

## What Lives Where

- `agents/`: agent role definitions and ownership boundaries
- `.claude/commands/`: Claude Code slash-command workflows
- `config/`: machine-readable policy, including validation profiles
- `docs/architecture/`: boundaries, toolchain, and extension patterns
- `docs/workflows/`: handoff, validation, PR, and incident workflows
- `docs/plans/`: active and completed execution plans
- `artifacts/validations/`: validation records and templates
- `tools/`: Python, Go, and C++ scaffolds
- `scripts/`: repo-local build, test, and lint entrypoints for agents

## Primary Commands

Run the repo-local scripts directly:

```bash
bash scripts/build.sh
bash scripts/test.sh
bash scripts/lint.sh
```

If `make` is installed, the top-level `Makefile` is a strict wrapper around the same flows.

## Planning And Validation

Non-trivial work should leave repository artifacts:

- active plan: [docs/plans/active/README.md](/home/ubuntu/claude-agent-setup/docs/plans/active/README.md)
- plan template: [docs/plans/active/TEMPLATE.md](/home/ubuntu/claude-agent-setup/docs/plans/active/TEMPLATE.md)
- validation policy: [config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml)
- validation template: [artifacts/validations/TEMPLATE.md](/home/ubuntu/claude-agent-setup/artifacts/validations/TEMPLATE.md)
- restriction policy: [docs/references/restrictions.md](/home/ubuntu/claude-agent-setup/docs/references/restrictions.md)
- production gate: [docs/references/production-gate.md](/home/ubuntu/claude-agent-setup/docs/references/production-gate.md)
- metrics summary: [artifacts/metrics/summary.json](/home/ubuntu/claude-agent-setup/artifacts/metrics/summary.json)

## Maintenance Rule

When root files and `docs/` disagree, update the root file to point at `docs/`, not to duplicate more detail.
