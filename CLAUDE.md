# claude-agent-setup

Multi-language agent toolkit with Python, Go, and C++ support.
Provides structured agent roles, tool permissions, and reusable skills.

---

## Architecture

This project follows a **layered agent architecture**:

```
┌─────────────────────────────────────────┐
│           Orchestrator Agent            │  ← coordinates sub-agents
├──────────┬──────────────┬───────────────┤
│  Python  │      Go      │     C++       │  ← language-specific agents
│  Agent   │    Agent     │    Agent      │
├──────────┴──────────────┴───────────────┤
│              Tool Layer                 │  ← shared tools & skills
│   (build, test, lint, benchmark)        │
└─────────────────────────────────────────┘
```

Agent definitions live in `agents/`. Tool implementations live in `tools/`.
Permission rules live in `.claude/settings.json`.

---

## Tech Stack

- **Python 3.11+** — scripting, data processing, ML tooling
- **Go 1.22+** — CLI tools, services, performance-critical agents
- **C++17** — low-level tools, bindings, native performance
- **Build:** `make` (top-level), `cmake` (C++), `go build`, `uv`/`pip`

---

## Project Structure

```
claude-agent-setup/
├── CLAUDE.md                  # This file — read by all agents
├── .claude/
│   ├── settings.json          # Tool allow/deny rules
│   └── commands/              # Custom slash commands
│       ├── build.md
│       ├── test.md
│       └── audit.md
├── agents/
│   ├── orchestrator.md        # Top-level coordination agent
│   ├── python-agent.md        # Python-specific agent profile
│   ├── go-agent.md            # Go-specific agent profile
│   └── cpp-agent.md           # C++-specific agent profile
├── tools/
│   ├── python/                # Python skills & utilities
│   ├── go/                    # Go tools
│   └── cpp/                   # C++ tools
└── config/
    ├── permissions.yaml       # Human-readable permission reference
    └── agents.yaml            # Agent capability matrix
```

---

## Running Tools

```bash
# Python
cd tools/python && uv run python skills.py

# Go
cd tools/go && go run .

# C++
cd tools/cpp && cmake -B build && cmake --build build
```

---

## Agent Roles

| Agent | Responsibilities | Can modify |
|-------|-----------------|------------|
| `orchestrator` | Breaks down tasks, delegates | `agents/`, `config/` |
| `python-agent` | Python code, scripts, ML | `tools/python/`, `*.py` |
| `go-agent` | Go services, CLI tools | `tools/go/`, `*.go` |
| `cpp-agent` | Native tools, bindings | `tools/cpp/`, `*.cpp`, `*.h` |

Agents operate within their language boundary unless explicitly granted cross-agent access.

---

## Permissions Model

Access is controlled via `.claude/settings.json`.
See `config/permissions.yaml` for the full documented reference.

**Quick reference:**
- `allow` — tools/patterns Claude can use without prompting
- `deny` — tools/patterns always blocked
- Per-agent overrides are set in `config/agents.yaml`

---

## Code Conventions

### Python
- Formatter: `ruff format`, linter: `ruff check`
- Type hints required on all public functions
- Tests: `pytest`, files named `test_*.py`

### Go
- Formatter: `gofmt` / `goimports`
- Errors wrapped with `fmt.Errorf("context: %w", err)`
- Tests: `go test ./...`, files named `*_test.go`

### C++
- Standard: C++17
- Formatter: `clang-format` (`.clang-format` in root)
- Build system: CMake, no raw Makefiles in `tools/cpp/`

---

## Hard Rules (apply to all agents)

- Never modify files outside the agent's designated scope without explicit instruction
- Never run destructive commands (`rm -rf`, `DROP TABLE`, `kill -9`) without confirmation
- Never commit secrets, tokens, or credentials
- Never bypass `.claude/settings.json` deny rules
- Always run tests before marking a task complete
