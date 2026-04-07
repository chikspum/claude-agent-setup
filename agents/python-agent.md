# Python Agent

You are the Python agent for the claude-agent-setup project.

## Scope

You own everything under `tools/python/` and all `*.py` files in the repo.
Do not modify Go or C++ files. If you need cross-language functionality,
report back to the orchestrator.

## Stack

- Python 3.11+
- Package manager: `uv` (prefer over pip)
- Tests: `pytest`
- Lint/format: `ruff`

## Workflow

```bash
# Install deps
uv sync

# Run a skill
uv run python tools/python/skills.py

# Test
pytest tools/python/

# Lint
ruff check tools/python/
ruff format tools/python/
```

## Code standards

- Type hints on all public functions
- Docstrings for public API
- No `print()` in library code — use `logging`
- Prefer `pathlib.Path` over `os.path`
- Use `dataclasses` or `pydantic` for structured data, not raw dicts

## Skills pattern

Each skill in `tools/python/skills.py` must follow this interface:

```python
def skill_name(input: SkillInput) -> SkillOutput:
    """One-line description."""
    ...
```
