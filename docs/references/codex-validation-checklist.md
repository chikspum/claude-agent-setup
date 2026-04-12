# Codex Validation Checklist

Use this checklist after every non-trivial Claude Code execution.

## Scope

- [ ] changed files are in scope
- [ ] no unrelated files were modified
- [ ] public interfaces remain within requested constraints

## Verification

- [ ] `git status --short`
- [ ] `git diff --stat`
- [ ] `git diff`
- [ ] relevant tests rerun by Codex
- [ ] relevant lint/build rerun by Codex when available

## Reporting

- [ ] missing tools or environment gaps explicitly called out
- [ ] skipped checks explicitly called out
- [ ] acceptance or rejection recorded
- [ ] validation artifact created or updated for non-trivial work
