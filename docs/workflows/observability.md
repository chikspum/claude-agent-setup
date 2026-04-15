# Observability

Rules for run logs, scorecard updates, and machine-readable metrics in the hybrid workflow.

## Purpose

Observability artifacts let Codex and future agents determine whether the workflow is actually improving — not just whether more process files exist.
A task with no run log is harder to audit retroactively.
A scorecard with gaps makes trends invisible.

## Run Log Rules

### When to create a run log

Create a run log for any execution that is **material**. An execution is material if it meets at least one of:

- at least one file was changed (docs, code, config, or templates)
- a non-trivial command was run and the result matters (tests, lint, build, JSON validation)
- the execution was blocked or partially blocked and that state should be recorded
- the task maps to an active plan file

Omit a run log for:
- trivial read-only explorations that produced no output
- single-sentence corrections that Codex applied inline with no Claude delegation

### Required fields

Every run log must populate these template keys from `artifacts/runs/TEMPLATE.md`:

| Key | Required value |
|-----|----------------|
| `run_id` | `YYYY-MM-DD-<task-id>-run-NN` |
| `date` | ISO date |
| `operator` | `Codex` or `Claude Code` |
| `task_id` | matches the plan or tracked task |
| `plan_file` | path, or `n/a` if no plan |
| `status` | `completed`, `blocked`, or `partial` |
| `Commands Run` | at least one row, even if result is SKIPPED |
| `Files Touched` | list every changed file, or `none` |

Fields may be left blank only if genuinely not applicable. Do not leave them blank as a shortcut.

### Naming convention

```
artifacts/runs/YYYY-MM-DD-<task-id>-run-NN.md
```

- Use the task-id from the plan file (snake_case or kebab-case matching the plan).
- Start at `run-01`. Increment for repeated attempts on the same task in the same day.
- If a task spans multiple days, use the date of each execution attempt.

### Creating a run log during a hybrid command

When Claude Code executes a hybrid command for a material task, the final output should include the run-log path. If no run log exists for the current execution, Claude Code should create one before reporting done.

The canonical trigger: any `/hybrid-*` command that changes files or runs non-trivial checks is material.

## Validation Artifact Rules

Validation artifacts are Codex's acceptance record, not Claude's self-report.

- Codex creates or updates the validation artifact after reviewing `git diff` and rerunning checks.
- Claude Code should name the expected path and leave it for Codex to populate.
- Template: `artifacts/validations/TEMPLATE.md`
- Naming: `artifacts/validations/YYYY-MM-DD-<task-id>.md`

Claude Code may pre-populate a validation artifact skeleton if the task brief calls for it, but the `Acceptance Decision` field must be left empty until Codex confirms.

## Scorecard Update Rules

The scorecard at `docs/quality/scorecard.md` uses a simple table format.

### When to add a row

Add a new scorecard row when:

- a plan moves from `active` to `completed`, or
- a Codex-accepted run log is created for a material task

Do not add rows for proposed or in-progress work.

### How to derive each column

| Column | Source |
|--------|--------|
| Date | date on the run log or validation artifact |
| Completed Plans | count files under `docs/plans/completed/` |
| Logged Runs | count files under `artifacts/runs/` excluding `README.md` and `TEMPLATE.md` |
| Validation Artifacts | count files under `artifacts/validations/` excluding `.gitkeep`, `README.md`, and `TEMPLATE.md` |
| Environment-Blocked Runs | count run logs where `status: blocked` or `unexpected_failures` is non-empty |
| Notes | one sentence on what changed or what was notable |

Columns must be derivable from actual artifacts. Never project or estimate.

### Machine-readable companion

After a scorecard row is added, update `artifacts/metrics/summary.json` to match:

- `artifact_counts.completed_plans`
- `artifact_counts.run_logs`
- `artifact_counts.validation_artifacts`
- `artifact_counts.environment_blocked_runs`

Update `generated_at` to the current date. Do not change `release_gate` fields unless a gate criterion has actually changed.

## Observability Fields: Machine-Readable Roadmap

The following fields are candidates to extract into structured form in a future phase:

| Field | Current location | Future form |
|-------|-----------------|-------------|
| `status` per run | run log free text | `artifacts/runs/` JSON sidecar |
| `missing_tools` | run log free text | `artifact_counts.environment_blocked_runs` extension |
| `acceptance_decision` | validation artifact free text | `artifacts/validations/` JSON sidecar |
| scorecard row | scorecard table | `summary.json` extended schema |

Do not implement these now. Note them here so a future agent has explicit targets rather than guessing what to automate.

## Checking Observability Completeness

To verify that observability is in good shape:

1. Every completed plan under `docs/plans/completed/` should have a corresponding validation artifact.
2. Every material Claude execution should have a run log.
3. `summary.json` counts should match actual artifact counts.
4. Scorecard rows should not be ahead of validated, committed artifacts.

Run `python3 scripts/check_artifacts.py` to catch artifact structure violations.
Run `python3 scripts/generate_metrics_summary.py --check` to catch summary drift.
