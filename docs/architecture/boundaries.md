# Boundaries

Ownership and editing boundaries for the repository.

## Agent Boundaries

- `orchestrator`: `agents/`, `config/`, and top-level coordination docs
- `python-agent`: `tools/python/` and Python files
- `go-agent`: `tools/go/` and Go files
- `cpp-agent`: `tools/cpp/` and C++ files

For Codex to Claude tandem work:

- Codex owns planning, acceptance criteria, and validation
- Claude Code owns bounded execution inside the brief Codex provides

## Practical Scope Rules

- do not change files outside the explicit handoff scope unless the brief says to
- if a task becomes cross-language, stop treating it as a single unstructured edit
- keep documentation updates adjacent to the code or workflow they describe
- if a task needs more than a few hundred lines or more than roughly one engineer-hour, split it into multiple plan items

## Escalation

Escalate or split work when:

- public interfaces would change
- ownership crosses language boundaries
- destructive git or environment actions are involved
- validation requirements are unclear
