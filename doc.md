# Claude Agent Setup Documentation Map

## About
`claude-agent-setup` is a hybrid agent workflow repository. This file is a routing map for agents, not a second operating manual.

## Read This When
- You need project-wide orientation before changing code or workflow behavior.
- You need to understand where bridge logic, policy, plans, artifacts, slash commands, and tool scaffolds live.
- You want the default documentation read order as an agent.

## Related Docs
- `./scripts/doc.md`
- `./docs/doc.md`
- `./tools/doc.md`
- `./artifacts/doc.md`
- `./config/doc.md`
- `./.claude/commands/DOC.md`
- `./agents/doc.md`

## Key Files
- `AGENTS.md` - root read-order entrypoint.
- `DOC.md` - root pointer into durable documentation.
- `codex-claude-code-doc.md` - machine-readable project operating model.
- `scripts/run_claude_from_plan.py` - bridge runner for plan-driven Claude execution.
- `scripts/delegate_to_claude.py` - plan generator plus bridge delegator.
- `config/validation.yaml` - machine-readable validation policy.

## Invariants
- Root docs are entrypoints and maps; durable detail belongs under `docs/`.
- This file should route work, not restate full Codex or Claude operating policy.
- Non-trivial work should leave plan, run-log, and validation artifacts.

## Global Workflow
1. Read the nearest `doc.md` before editing.
2. Follow adjacent `Related Docs` when the change crosses boundaries.
3. Read the durable workflow or reference doc behind the area you will change.
4. Use the repo-local verification surface for the touched area.

## Change Routing Guide
- Bridge runner or delegation behavior: read `scripts/doc.md`, then `docs/workflows/hybrid-execution.md`, then tests.
- Validation, restrictions, or production policy: read `config/doc.md`, `docs/doc.md`, then the relevant reference doc.
- Claude slash-command behavior or handoff semantics: read `docs/doc.md`, `.claude/commands/`, and `scripts/doc.md`.
- Tool scaffold or Python test changes: read `tools/doc.md`, then the nearest language/tool files.
- Artifact, plan, or observability changes: read `artifacts/doc.md`, then `docs/doc.md`.

## Verification Matrix
- Bridge or orchestration change: run focused bridge tests plus `py_compile` and `ruff`.
- Docs-map or policy-routing change: re-read the affected `doc.md` files and run docs-drift or policy checks if needed.
- Validation or production-gate change: run the relevant repo policy checks and, if needed, `make verify`.

## Project Map
- `scripts/` contains bridge runners, repo verification entrypoints, and policy automation.
- `docs/` is the durable system of record for architecture, workflows, references, plans, and quality guidance.
- `config/` contains machine-readable validation and agent policy.
- `agents/` defines agent roles and ownership boundaries.
- `.claude/commands/` contains Claude Code slash-command workflows used in the hybrid model.
- `tools/` contains Python, Go, and C++ scaffolds plus tests for agent-facing tool paths.
- `artifacts/` stores run logs, validation records, metrics, and debug output.
- `cctest/` is the disposable Claude bridge test workspace.
- `ccwork/` is the disposable Claude bridge working directory for real runs.

## Body
The practical read order for most changes is:
- `doc.md`
- the nearest subsystem `doc.md`
- the relevant durable workflow or reference doc under `docs/`
- the actual implementation and tests

Use the root maps only to route into the right local doc and the right durable workflow page. If you start copying detailed policy here, the repo will drift again and future agents will have to reconcile multiple overlapping summaries.
