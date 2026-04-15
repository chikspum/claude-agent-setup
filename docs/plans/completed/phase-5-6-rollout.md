# Phase 5-6 Rollout

## Metadata

- task_id: phase-5-6-rollout
- status: completed
- owner: Codex
- last_updated: 2026-04-08

## Problem

Phase 5 and Phase 6 were only partially represented in the repo.

The repo had templates and workflow docs, but the plan lifecycle was not finished end to end, root docs still duplicated `docs/`, and the documented build/test/lint surface was not agent-friendly in environments missing `make` or parts of the language toolchain.

## Context

Relevant files:

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `DOC.md`
- `docs/index.md`
- `docs/plans/active/`
- `docs/plans/completed/`
- `docs/architecture/toolchain.md`
- `docs/references/command-reference.md`
- `config/validation.yaml`
- `Makefile`
- `scripts/`

Environment observations from this workspace:

- `make` is not installed
- `pytest`, `go`, and `g++` are available
- `uv`, `ruff`, `cmake`, `ctest`, and `clang-format` are not installed

## Scope

- files expected to change:
  - root agent docs and root documentation map
  - plan lifecycle docs and example plan
  - repo-local build/test/lint entrypoints
  - toolchain and command reference docs
- files that must not change:
  - language scaffold source behavior in `tools/`
  - agent ownership policy in `config/agents.yaml`
- public interfaces that must remain stable:
  - top-level `make build`, `make test`, and `make lint` names
- dependencies or tools that may be missing locally:
  - `make`
  - `uv`
  - `ruff`
  - `cmake`
  - `ctest`
  - `clang-format`

## Milestones

1. [x] Formalize plan lifecycle across `active/` and `completed/`.
2. [x] Reduce root-doc duplication and make root files point into `docs/`.
3. [x] Add repo-local build/test/lint scripts with explicit missing-tool reporting and fallbacks.
4. [x] Record a validation artifact for this rollout and leave the plan usable as an active example.

## Claude Work Items

- none required; work was completed directly in Codex

## Validation Strategy

- run `bash scripts/build.sh`
- run `bash scripts/test.sh`
- run `bash scripts/lint.sh`
- re-read `docs/index.md`, `docs/plans/active/README.md`, and `docs/architecture/toolchain.md`
- acceptance criteria:
  - root docs no longer restate large sections already covered by `docs/`
  - at least one real active plan exists
  - `docs/plans/completed/` exists with lifecycle guidance
  - build/test/lint entrypoints work directly via `bash scripts/*.sh`
- validation artifact path:
  - `artifacts/validations/phase-5-6-rollout.md`

## Risks

- fallback-based lint/build behavior can hide the difference between full and degraded validation if docs are unclear
- future contributors may keep editing root docs unless the entrypoint rule stays explicit

## Execution Notes

- converted root docs into maps and policy files instead of long duplicated manuals
- chose `scripts/*.sh` as the primary agent entrypoints because `make` is not guaranteed in local environments
- kept `Makefile` as a strict wrapper for environments that do have `make`
- recorded validation in `artifacts/validations/phase-5-6-rollout.md`
- archived this plan after opening the next active plan for phase 7

## Exit Criteria

- active plan is usable by another agent without extra explanation
- repo-local command surface is documented and runnable
- remaining work is limited to archival and validation artifact follow-through

## Archive Footer

- completion date: 2026-04-08
- validation artifact: [artifacts/validations/phase-5-6-rollout.md](/home/ubuntu/claude-agent-setup/artifacts/validations/phase-5-6-rollout.md)
- run log: [artifacts/runs/2026-04-08-phase-5-6-rollout-run-01.md](/home/ubuntu/claude-agent-setup/artifacts/runs/2026-04-08-phase-5-6-rollout-run-01.md)
- next active plan: [docs/plans/active/phase-7-observability-bootstrap.md](/home/ubuntu/claude-agent-setup/docs/plans/active/phase-7-observability-bootstrap.md)
