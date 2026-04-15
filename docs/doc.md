# Durable Documentation

## About
`docs/` is the durable system of record for architecture, workflows, references, quality guidance, and plan lifecycle in this repository.

## Read This When
- You need the canonical workflow or policy explanation behind a script or root entrypoint.
- You are updating plans, references, validation guidance, or production-readiness docs.
- You need to understand what future agents are expected to read before editing.

## Related Docs
- `../doc.md`
- `../config/doc.md`
- `../artifacts/doc.md`
- `../scripts/doc.md`

## Key Files
- `index.md` - global docs index.
- `workflows/hybrid-execution.md` - Codex to Claude handoff model.
- `workflows/validation.md` - validation and acceptance workflow.
- `references/claude-cli-handoff.md` - practical bridge invocation and abnormal-run semantics.
- `references/restrictions.md` - restriction policy and VCS gate.
- `plans/active/TEMPLATE.md` - plan template for non-trivial work.

## Invariants
- `docs/` is the durable source of truth; root files should point here rather than duplicate it.
- Workflow docs should describe behavior the scripts and policies actually implement.
- Reference docs must stay aligned with the bridge runner, validation policy, and restriction model.

## Workflow
- Read `index.md` first when you need a broad map.
- Use `workflows/` for process and execution semantics.
- Use `references/` for command contracts, policy surfaces, and machine-facing guidance.
- Use `plans/` for task lifecycle state and `quality/` for acceptance framing.

## Verification
- For docs-only routing updates, re-read the affected map and linked docs for consistency.
- For workflow or policy changes that mirror scripts, validate the corresponding script/test path too.
- Use docs-drift and policy checks when the change affects root-to-doc consistency.

## Body
This directory is where future agents should land when a root map points them deeper. The main risk here is drift: a root entrypoint or machine-readable summary says one thing, while a workflow or reference doc says another. When changing docs here, prefer tightening the routing and invariants rather than expanding prose that duplicates implementation details.
