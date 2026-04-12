# Claude CLI Handoff

Practical note for running real Codex -> Claude handoffs in this repository.

## Recommended Invocation

Prefer `claude -p` with the prompt provided on `stdin`.

Example shape:

```bash
claude -p --permission-mode acceptEdits --add-dir /home/ubuntu/claude-agent-setup <<'EOF'
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
- invokes `claude -p` with `--add-dir /home/ubuntu/claude-agent-setup`
- prints a normalized runner header before Claude output so Codex can review the result consistently

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
