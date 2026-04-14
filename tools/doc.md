# Tool Scaffolds

## About
`tools/` contains agent-facing language scaffolds, helper modules, and tests used to prove that delegated code work and bridge-facing tool paths still function.

## Read This When
- You are changing Python tool scaffolds or their tests.
- You are debugging bridge tests or example implementation surfaces.
- You need to know whether a change belongs in Python, Go, or C++ scaffolding.

## Related Docs
- `../doc.md`
- `../scripts/doc.md`
- `../docs/doc.md`

## Key Files
- `python/pyproject.toml` - Python package and dev dependency surface.
- `python/test_claude_bridge_runner.py` - focused tests for bridge classification and orchestration behavior.
- `python/pagination_tool.py` - current Python example tool path.
- `python/skills.py` - Python helper surface used by tests/examples.

## Invariants
- Tool scaffolds are examples and test surfaces, not the primary workflow source of truth.
- Bridge tests under `tools/python/` must stay aligned with actual runner behavior in `scripts/`.
- Language-specific scaffolds should stay localized; do not leak tool-specific assumptions into repo-global workflow docs unless they are intentionally promoted.

## Workflow
- For bridge regressions, start with `python/test_claude_bridge_runner.py`.
- For Python package changes, read `pyproject.toml` and the nearest tests before editing.
- For non-Python scaffolds, stay within the relevant language subdirectory and keep changes bounded.

## Verification
- Python: `uv run --extra dev pytest -q test_claude_bridge_runner.py`
- Python lint: `uv run --extra dev ruff check ...`
- If the change touches another language scaffold, use the nearest repo-local build/test entrypoint.

## Body
This directory exists so the hybrid agent workflow has concrete, testable code surfaces instead of pure documentation. The Python subtree matters the most today because the bridge runner and its focused tests live there. Treat it as the quickest place to prove bridge behavior, validation rules, and bounded delegated edits.
