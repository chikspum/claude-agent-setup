# Phase 7 Observability Bootstrap

## Metadata

- task_id: phase-7-observability-bootstrap
- status: active
- owner: Codex
- last_updated: 2026-04-09

## Problem

The repository now has plans and validation artifacts, but hybrid execution observability is still minimal.

Without stable run logging and scorecard updates, it is hard to tell whether the workflow is improving or just producing more process artifacts.

## Context

Relevant files:

- `artifacts/runs/`
- `artifacts/validations/`
- `docs/quality/scorecard.md`
- `docs/workflows/hybrid-execution.md`
- `.claude/commands/handoff.md`
- `.claude/commands/hybrid-test.md`
- `.claude/commands/hybrid-commit.md`
- `.claude/commands/hybrid-pr.md`

## Scope

- files expected to change:
  - observability docs and artifact templates
  - hybrid command docs that emit run-log-friendly output
  - scorecard summaries
- files that must not change:
  - language scaffold implementation under `tools/`
  - validation policy semantics in `config/validation.yaml` unless a concrete gap is discovered
- public interfaces that must remain stable:
  - existing command names
  - validation artifact structure already in use
- dependencies or tools that may be missing locally:
  - none required beyond current shell tooling

## Milestones

1. [x] Normalize run-log creation rules across hybrid commands.
2. [x] Add at least one more completed task with run-log and validation coverage.
3. [x] Expand the scorecard from a baseline row to a recurring reporting format.
4. [x] Decide which observability fields should become machine-readable later.

## Claude Work Items

- polish hybrid command wording if Codex delegates command-doc refinement
- generate run logs for future delegated executions when asked

## Validation Strategy

- re-read `docs/workflows/hybrid-execution.md`
- re-read `docs/quality/scorecard.md`
- ensure new hybrid commands mention plan, validation, and run-log context consistently
- acceptance criteria:
  - observability rules are explicit enough for another agent to follow
  - scorecard updates can be derived from actual artifacts in the repo

## Risks

- too much logging overhead can make small tasks slower than the value of the data collected
- free-form run logs may drift unless a stronger template discipline is maintained

## Execution Notes

- created after archiving the phase 5 and 6 rollout
- intended as the next repository-facing task rather than a speculative placeholder
- milestone progress improved after completing `command-surface-alignment`
- first real Claude delegation completed via `claude-handoff-smoke`; template keys now use stable snake_case names
- delegated code-edit loop validated via `python-reverse-skill`
- production-ready machine-readable metrics summary added via `production-prep`

## Exit Criteria

- run logging is routine for material tasks
- scorecard reflects at least a small history of actual executions
- future automation targets are clear from the artifacts already in the repo
