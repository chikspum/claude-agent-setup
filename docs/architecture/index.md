# Architecture Index

Repository architecture guidance for both Codex and Claude Code.

## Read Next

- [boundaries.md](/home/ubuntu/claude-agent-setup/docs/architecture/boundaries.md) for ownership and change scope
- [toolchain.md](/home/ubuntu/claude-agent-setup/docs/architecture/toolchain.md) for build, test, and lint expectations

## Summary

This repository is a multi-language agent toolkit with:

- agent profiles in `agents/`
- Claude configuration in `.claude/`
- machine-readable capabilities in `config/`
- language scaffolds in `tools/python/`, `tools/go/`, and `tools/cpp/`

The important architectural rule is separation of concerns:

- Codex manages planning and validation
- Claude Code executes scoped implementation work
- language ownership remains explicit and should not be blurred by convenience edits
