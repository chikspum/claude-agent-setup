# Docs Index

This directory is the system of record for detailed, durable workflow guidance.

Start here when root agent files point you into deeper material.

## Root Machine-Readable Doc

- [../codex-claude-code-doc.md](/home/ubuntu/claude-agent-setup/codex-claude-code-doc.md)

## Architecture

- [architecture/index.md](/home/ubuntu/claude-agent-setup/docs/architecture/index.md)
- [architecture/boundaries.md](/home/ubuntu/claude-agent-setup/docs/architecture/boundaries.md)
- [architecture/toolchain.md](/home/ubuntu/claude-agent-setup/docs/architecture/toolchain.md)

## Workflows

- [workflows/hybrid-execution.md](/home/ubuntu/claude-agent-setup/docs/workflows/hybrid-execution.md)
- [workflows/validation.md](/home/ubuntu/claude-agent-setup/docs/workflows/validation.md)
- [workflows/observability.md](/home/ubuntu/claude-agent-setup/docs/workflows/observability.md)
- [workflows/pr-flow.md](/home/ubuntu/claude-agent-setup/docs/workflows/pr-flow.md)
- [workflows/incident-debugging.md](/home/ubuntu/claude-agent-setup/docs/workflows/incident-debugging.md)

## Plans

- [plans/active/README.md](/home/ubuntu/claude-agent-setup/docs/plans/active/README.md)
- [plans/active/TEMPLATE.md](/home/ubuntu/claude-agent-setup/docs/plans/active/TEMPLATE.md)
- [plans/active/phase-7-observability-bootstrap.md](/home/ubuntu/claude-agent-setup/docs/plans/active/phase-7-observability-bootstrap.md)
- [plans/completed/README.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/README.md)
- [plans/completed/2026-04-09-command-surface-alignment.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/2026-04-09-command-surface-alignment.md)
- [plans/completed/2026-04-09-claude-handoff-smoke.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/2026-04-09-claude-handoff-smoke.md)
- [plans/completed/2026-04-09-python-reverse-skill.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/2026-04-09-python-reverse-skill.md)
- [plans/completed/phase-5-6-rollout.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/phase-5-6-rollout.md)
- [plans/completed/2026-04-12-production-prep.md](/home/ubuntu/claude-agent-setup/docs/plans/completed/2026-04-12-production-prep.md)

## Quality

- [quality/test-matrix.md](/home/ubuntu/claude-agent-setup/docs/quality/test-matrix.md)
- [quality/scorecard.md](/home/ubuntu/claude-agent-setup/docs/quality/scorecard.md)

## Validation Artifacts

- [../artifacts/validations/TEMPLATE.md](/home/ubuntu/claude-agent-setup/artifacts/validations/TEMPLATE.md)
- [../config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml)
- [../artifacts/runs/README.md](/home/ubuntu/claude-agent-setup/artifacts/runs/README.md)
- [../artifacts/runs/TEMPLATE.md](/home/ubuntu/claude-agent-setup/artifacts/runs/TEMPLATE.md)

## References

- [references/claude-brief-template.md](/home/ubuntu/claude-agent-setup/docs/references/claude-brief-template.md)
- [references/claude-cli-handoff.md](/home/ubuntu/claude-agent-setup/docs/references/claude-cli-handoff.md)
- [references/codex-runtime-profiles.md](/home/ubuntu/claude-agent-setup/docs/references/codex-runtime-profiles.md)
- [references/codex-validation-checklist.md](/home/ubuntu/claude-agent-setup/docs/references/codex-validation-checklist.md)
- [references/command-reference.md](/home/ubuntu/claude-agent-setup/docs/references/command-reference.md)
- [references/env-setup.md](/home/ubuntu/claude-agent-setup/docs/references/env-setup.md)
- [references/restrictions.md](/home/ubuntu/claude-agent-setup/docs/references/restrictions.md)
- [references/production-gate.md](/home/ubuntu/claude-agent-setup/docs/references/production-gate.md)

## Automation

- `make doctor`: strict toolchain presence and minimum versions
- `make policy-check`: validation-artifact and docs-drift enforcement
- `make metrics-check`: machine-summary drift detection
- `make verify`: full strict verification gate
- `make handoff PLAN=...`: run Claude Code against a repository plan through the bridge runner
- `make delegate GOAL=...`: let Codex create a temporary bounded plan and delegate it to Claude

## Hybrid Commands

Project-level Claude commands live in `.claude/commands/`.
Use the hybrid variants when Codex is supervising the workflow:

- `/handoff`
- `/hybrid-doc`
- `/hybrid-test`
- `/hybrid-fix`
- `/hybrid-commit`
- `/hybrid-pr`
