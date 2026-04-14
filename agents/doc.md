# Agent Roles And Ownership

## About
`agents/` contains agent-specific role prompts and ownership boundaries used by the hybrid workflow.

## Read This When
- You need to know which agent should own a change.
- You are updating role definitions or specialization boundaries.
- You are aligning repo behavior with `config/agents.yaml`.

## Related Docs
- `../doc.md`
- `../config/doc.md`
- `../CODEX.md`
- `../CLAUDE.md`

## Key Files
- `orchestrator.md` - top-level coordination role.
- `python-agent.md` - Python ownership and execution expectations.
- `go-agent.md` - Go ownership and execution expectations.
- `cpp-agent.md` - C++ ownership and execution expectations.
- `codex-init.md` - repository bootstrap prompt used for Codex-oriented setup.

## Invariants
- Role prompts should agree with `config/agents.yaml`.
- Ownership boundaries should reduce overlap and ambiguity, not create duplicate sources of truth.
- Agent docs define responsibility routing; they should not silently override repo-wide validation or restriction policy.

## Workflow
1. Read the relevant role file before changing its owned surface.
2. Cross-check `config/agents.yaml` for machine-readable ownership and capability rules.
3. If a boundary changes, update both the prompt and the registry view.
4. Re-check root docs if the change affects the repo-wide operating model.

## Verification
- Re-read `config/agents.yaml` and the relevant root workflow docs after changing an agent role.
- If the role change affects how work is delegated, verify the bridge and handoff docs still route tasks correctly.

## Body
This directory is the human-readable side of agent ownership. In practice, most failures here are routing failures: the wrong agent owns a path, role prompts promise capabilities that the repo does not support, or ownership overlaps so much that another agent cannot tell where to start. Keep these files clear, bounded, and consistent with the registry.
