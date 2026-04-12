# Codex Init For Claude Tandem

Use this file as the bootstrap instruction set for any Codex agent that will work with Claude Code in this repository.

## Init Objective

Initialize the Codex agent so it can manage Claude Code as a worker while retaining validation ownership.

## Init Rules

1. Read [CODEX.md](/home/ubuntu/claude-agent-setup/CODEX.md), [CLAUDE.md](/home/ubuntu/claude-agent-setup/CLAUDE.md), and [config/agents.yaml](/home/ubuntu/claude-agent-setup/config/agents.yaml) before delegating anything.
2. Treat Claude Code as an executor, not as the final reviewer.
3. Always inspect the repository locally before writing the prompt for Claude Code.
4. Build a concrete plan before invoking Claude Code.
5. Re-run validation commands yourself after Claude Code changes the workspace.
6. If Claude Code produces a mostly-correct diff with a small defect, patch it directly instead of re-delegating by default.
7. Use Claude Code slash commands intentionally:
   - `/doc` for documentation updates
   - `/review` for an auxiliary pass
   - `/test` for repository test flow
   - `/commit` after Codex validation
   - `/pr` after Codex validation
8. If `claude init` is needed, inspect generated files before accepting them as repository policy.

## Init Sequence

When starting work in this repo, a Codex agent should follow this sequence:

1. Read the target task and inspect relevant files locally.
2. Decide whether the task should stay local or be delegated to Claude Code.
3. If delegating, write a constrained execution brief with:
   - goal
   - target files
   - forbidden files
   - verification commands
   - expected final response format
4. Run Claude Code.
5. Inspect `git diff`.
6. Run tests, lint, or build commands yourself.
7. Only then report status to the user.

## `claude init` Guidance

If a Codex agent needs to initialize Claude Code support in a fresh clone:

1. Run `claude init` in the repository root.
2. Inspect generated Claude configuration files.
3. Check for overlap or conflict with [CLAUDE.md](/home/ubuntu/claude-agent-setup/CLAUDE.md), `.claude/commands/`, and [CODEX.md](/home/ubuntu/claude-agent-setup/CODEX.md).
4. Keep repository-specific workflow rules in `CODEX.md`; do not let generic init output override them silently.
5. If init creates noisy generic content, trim it before treating setup as complete.

## Minimum Validation Standard

Before considering Claude Code output acceptable, the Codex agent must confirm:

- changed files are in scope
- tests relevant to the task were run
- any skipped verification is explicitly explained
- generated documentation does not overstate repository capabilities

## Reporting Standard

When reporting back after Claude Code execution, the Codex agent should provide:

- what Claude Code was asked to do
- what files actually changed
- what validation Codex performed
- what remains uncertain or blocked
