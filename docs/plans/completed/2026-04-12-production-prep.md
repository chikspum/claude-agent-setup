# Production Prep

## Metadata

- task_id: production-prep
- status: completed
- owner: Codex
- last_updated: 2026-04-12

## Problem

The repository had working hybrid-agent building blocks, but it still needed a production-default operating model, explicit runtime-versus-policy guidance, and machine-readable observability output for internal team use.

## Context

Relevant files:

- `CODEX.md`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/workflows/hybrid-execution.md`
- `docs/workflows/pr-flow.md`
- `docs/references/command-reference.md`
- `docs/references/claude-cli-handoff.md`
- `docs/references/env-setup.md`
- `docs/quality/scorecard.md`
- `artifacts/runs/`
- `artifacts/validations/`

## Scope

- files expected to change:
  - operating-model docs
  - production reference docs
  - machine-readable metrics summary
- files that must not change:
  - tool implementations under `tools/`
  - Claude command names
  - validation policy semantics in `config/validation.yaml`
- public interfaces that must remain stable:
  - `Codex -> Claude Code` operating model
  - existing artifact locations and command names

## Milestones

1. [x] Make the Codex-versus-Claude runtime boundary explicit in production docs.
2. [x] Add runtime profile and restriction policy references for internal-team production use.
3. [x] Add a machine-readable observability summary.
4. [x] Define a production release gate in-repo.

## Claude Work Items

- none required for this pass; work was documentation and metrics hardening done directly in Codex

## Validation Strategy

- validate `artifacts/metrics/summary.json` as JSON
- re-read operating model and production reference docs
- acceptance criteria:
  - command ownership is unambiguous
  - runtime-profile guidance is separate from restriction policy
  - production gate is documented
  - metrics summary matches current artifact state

## Risks

- repo-local policy still needs to be mirrored by the actual launcher or sandbox for hard guarantees
- future workflow changes can reintroduce drift if docs and metrics are not updated together

## Execution Notes

- production mode is now explicitly `Codex orchestrates Claude Code`
- Claude slash commands are now documented as Claude runtime features, not Codex-native built-ins
- machine-readable metrics summary was added as a complement to markdown artifacts

## Exit Criteria

- internal-team production mode is documented clearly enough for another engineer or agent to follow without guesswork
- observability is available in both markdown and machine-readable form

## Archive Footer

- completion date: 2026-04-12
- validation artifact: [artifacts/validations/2026-04-12-production-prep.md](/home/ubuntu/claude-agent-setup/artifacts/validations/2026-04-12-production-prep.md)
- run log: [artifacts/runs/2026-04-12-production-prep-run-01.md](/home/ubuntu/claude-agent-setup/artifacts/runs/2026-04-12-production-prep-run-01.md)
- related active plan: [docs/plans/active/phase-7-observability-bootstrap.md](/home/ubuntu/claude-agent-setup/docs/plans/active/phase-7-observability-bootstrap.md)
