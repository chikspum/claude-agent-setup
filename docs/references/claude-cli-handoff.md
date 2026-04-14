# Claude CLI Handoff

Practical note for running real Codex -> Claude handoffs in this repository.

## Recommended Invocation

Prefer `claude -p` with the prompt provided on `stdin`.
For bridge automation, prefer machine-readable output and disabled session persistence.

Example shape:

```bash
claude -p --output-format json --no-session-persistence --permission-mode acceptEdits --add-dir /home/ubuntu/claude-agent-setup <<'EOF'
<bounded handoff brief>
EOF
```

Repository bridge entrypoints:

```bash
bash scripts/run_claude_handoff.sh docs/plans/active/<plan-file>.md
make handoff PLAN=docs/plans/active/<plan-file>.md
python3 scripts/delegate_to_claude.py --goal "..." --change "path: exact change"
python3 scripts/delegate_to_claude.py --goal "..." --write-run-log-draft
python3 scripts/delegate_to_claude.py --goal "..." --write-run-log-draft --write-validation-draft
```

## Why This Pattern

- `stdin` is more reliable than passing a large multi-line prompt as a positional argument
- `--output-format json` gives Codex a stable machine-readable result channel when Claude exits cleanly
- `--no-session-persistence` avoids bridge runs lingering on session bookkeeping after the actual work is done
- `--add-dir` keeps the repository path explicit
- `--permission-mode acceptEdits` works for bounded edit tasks without forcing the fully permissive modes
- the brief stays easy to archive into plans, run logs, and validation artifacts

## Permission Notes

- `dontAsk` is useful as a probe when you want to confirm scope and prompt quality, but it will block file writes
- `acceptEdits` is the practical default for repo-local delegated work
- use stricter or broader modes intentionally; do not pick them by habit

## Supported Production Default

For internal team production use:

- Codex prepares the plan and brief
- Claude Code runs the bounded task
- `acceptEdits` is the default edit-capable permission mode
- `dontAsk` is not the default production mode for edit tasks

## Brief Requirements

A good handoff brief should include:

- plan path
- exact goal
- required file list
- forbidden file list
- constraints
- verification commands
- required final response format

Use [claude-brief-template.md](/home/ubuntu/claude-agent-setup/docs/references/claude-brief-template.md) as the base.

## Bridge Behavior

The repository bridge:

- reads the plan file
- derives a bounded Claude brief from the plan metadata, scope, work items, and validation strategy
- auto-selects `micro_probe`, `sliced_edit`, or `single_edit` orchestration mode from the delegated task shape
- invokes `claude -p` with `--output-format json`, `--no-session-persistence`, and `--add-dir /home/ubuntu/claude-agent-setup`
- prints a normalized runner header before Claude output so Codex can review the result consistently
- enforces a runtime timeout and can early-abort edit-capable runs that stall in an in-scope `path_created_only` state
- classifies bridge outcomes explicitly as `success`, `partial_success`, or `failure`
- writes a debug artifact under `artifacts/debug/claude-bridge/` for timed-out or otherwise abnormal edit runs

## Orchestration Modes

- `micro_probe`: compact read-only planning prompt with 2-3 probe items and a strict response shape
- `sliced_edit`: broad edit task is automatically narrowed to the first deterministic slice
- `single_edit`: already-bounded edit task can run as one handoff

For pagination-engine-like work, the default slice order is:

1. core models + fingerprinting + detector
2. runtime + navigator + browser helpers
3. tests + pyproject integration
4. docs, guarantees, and limitations

## Outcome Semantics

- `success`: Claude returned a clean final response and the bridge finished normally
- `partial_success`: Claude did not finish cleanly, but meaningful in-scope repository progress exists and the result is either already acceptable or salvageable via a narrow follow-up
- `failure`: Claude made no useful progress, or the observed changes are out-of-scope or clearly unsafe

Abnormal edit runs also carry a materialization state:

- `no_progress`
- `path_created_only`
- `file_materialized`
- `validated_partial`
- `validated_success`

`path_created_only` means the allowed package or directory path was created, but real file content did not materialize before the runner stopped the pass.
This is treated as recoverable only when the path stayed in scope and the runner can recommend a narrower next slice.

`partial_success` is not automatic acceptance.
It means the orchestrator found real bounded progress and preserved enough evidence for Codex to validate or recover the task with a narrower follow-up.

The delegate runner adds one higher layer:

- accepts a direct Codex goal plus optional scope flags
- generates a temporary bounded plan
- routes that plan through the same Claude bridge
- prints suggested run-log and validation-artifact paths before execution
- can write a draft run log automatically when `--write-run-log-draft` is used
- can write a draft validation artifact automatically when `--write-validation-draft` is used

## Validation Rule

Claude output is never final on its own.
Codex still has to:

- inspect the diff
- confirm files stayed in scope
- rerun or explicitly waive checks
- record a run log and validation artifact for non-trivial work
