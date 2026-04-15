# Command Surface Alignment

## Metadata

- task_id: command-surface-alignment
- status: completed
- owner: Codex
- last_updated: 2026-04-09

## Problem

The repository documented `scripts/build.sh`, `scripts/test.sh`, and `scripts/lint.sh` as the primary agent-friendly entrypoints, but the base Claude commands `/build`, `/test`, and `/status` still described the older direct toolchain flow.

That drift made the command layer less trustworthy and undermined the new plan, run-log, and validation workflow.

## Context

Relevant files:

- `.claude/commands/build.md`
- `.claude/commands/test.md`
- `.claude/commands/status.md`
- `docs/references/command-reference.md`
- `scripts/test.sh`
- `docs/workflows/hybrid-execution.md`
- `docs/quality/scorecard.md`
- `artifacts/runs/`
- `artifacts/validations/`

## Scope

- files expected to change:
  - base command docs for build, test, and status
  - `scripts/test.sh` fallback behavior if validation exposed a repo-local workflow bug
  - command reference and observability records tied to this task
- files that must not change:
  - language scaffold source code under `tools/`
  - command names and top-level script paths
- public interfaces that must remain stable:
  - `/build`
  - `/test`
  - `/status`
- dependencies or tools that may be missing locally:
  - `make`
  - `uv`
  - `ruff`
  - `cmake`
  - `ctest`
  - `clang-format`

## Milestones

1. [x] Rewrite `/build`, `/test`, and `/status` around repo-local scripts and degraded-mode reporting.
2. [x] Record the execution in a run log and validation artifact.
3. [x] Archive the completed task and update scorecard history.

## Claude Work Items

- none required; work was completed directly in Codex

## Validation Strategy

- re-read `.claude/commands/build.md`, `.claude/commands/test.md`, and `.claude/commands/status.md`
- run `bash scripts/build.sh`
- run `bash scripts/test.sh`
- run `bash scripts/lint.sh`
- acceptance criteria:
  - command docs match the repo-local command surface
  - status guidance distinguishes full validation from degraded mode
  - the task leaves run-log and validation records in the repo

## Risks

- over-specifying `/status` may make it harder to use flexibly in partial environments
- command docs may drift again if future script behavior changes without command updates

## Execution Notes

- created as the first real tracked task after phase 5 and 6 archival
- validation exposed a `Text file busy` race in `scripts/test.sh` when `build.sh` and `test.sh` ran concurrently
- fixed the fallback test binary path to use a process-unique file under `/tmp`

## Exit Criteria

- base command docs align with current repository reality
- the task is archived as a completed plan with validation evidence

## Archive Footer

- completion date: 2026-04-09
- validation artifact: [artifacts/validations/2026-04-09-command-surface-alignment.md](/home/ubuntu/claude-agent-setup/artifacts/validations/2026-04-09-command-surface-alignment.md)
- run log: [artifacts/runs/2026-04-09-command-surface-alignment-run-01.md](/home/ubuntu/claude-agent-setup/artifacts/runs/2026-04-09-command-surface-alignment-run-01.md)
- next active plan: [docs/plans/active/phase-7-observability-bootstrap.md](/home/ubuntu/claude-agent-setup/docs/plans/active/phase-7-observability-bootstrap.md)
