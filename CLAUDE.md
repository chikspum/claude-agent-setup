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
├── Makefile                   # Top-level build/test/lint targets
├── .gitignore                 # Git ignore rules
├── .env.example               # Environment variable template
├── .claude/
│   ├── settings.json          # Tool allow/deny rules + hooks
│   └── commands/              # Custom slash commands
│       ├── build.md           # /build — build all languages
│       ├── test.md            # /test — run all tests
│       ├── audit.md           # /audit — permission & security check
│       ├── review.md          # /review — code review for staged changes
│       ├── explain.md         # /explain <target> — explain how code works
│       ├── refactor.md        # /refactor <target> — safe refactoring
│       ├── security-scan.md   # /security-scan — deep vuln scan
│       ├── commit.md          # /commit — smart conventional commit helper
│       ├── pr.md              # /pr — generate and create a pull request
│       ├── fix.md             # /fix <error> — targeted bug fixer
│       ├── doc.md             # /doc <target> — generate/update documentation
│       ├── todo.md            # /todo — find and prioritize TODO/FIXME comments
│       ├── research.md        # /research <topic> — structured web research
│       ├── deps.md            # /deps — dependency health check
│       ├── status.md          # /status — project health dashboard
│       └── init.md            # /init <lang> <name> — scaffold new component
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

Access uses a **blocklist model**: everything is allowed by default except patterns
explicitly denied. See `.claude/settings.json` for the full deny list.

**How it works:**
- `deny` patterns in `.claude/settings.json` block dangerous operations globally (destructive shell commands, secret-leaking writes, etc.)
- **Hooks** enforce additional runtime safety:
  - `PreToolUse` — blocks writes to secret files (`.env`, `*.pem`, `*.key`, credentials, etc.)
  - `PostToolUse` — scans output for leaked tokens or secrets after each tool call
- WebFetch and WebSearch are **allowed globally** — no per-agent override needed

**Per-agent scoping** is done through each agent's `.md` profile (in `agents/`) and the
`owns` / `cannot_modify` fields in `config/agents.yaml`, not through `settings.json`
overrides.

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

**Go Tool Pattern — mandatory for all new tools in `tools/go/`:**

Every tool lives in its own subdirectory (`tools/go/<name>/`) and MUST export a
`Run` function with the exact signature below. Before writing a new tool,
**read `tools/go/tools.go` first** to get the `Args` and `Result` types.

```go
// tools/go/<name>/<name>.go
package <name>

import (
    "context"
    "fmt"

    tools "github.com/your-org/claude-agent-setup/tools/go"
)

// Run implements the standard tool interface.
func Run(ctx context.Context, args tools.Args) (tools.Result, error) {
    if args.Data == "" {
        return tools.Result{}, fmt.Errorf("<name>: Data must not be empty")
    }
    // your logic here
    return tools.Result{Output: "...", Success: true}, nil
}
```

Do NOT invent a custom struct (e.g. `Fetch`, `FetchMany`, `Config`) as the **primary
entry point**. The public API must be `Run(ctx context.Context, args tools.Args) (tools.Result, error)`.
Internal helper functions and types can be unexported or exported as needed, but
`Run` is the canonical entry point that orchestrators call.

### C++
- Standard: C++17
- Formatter: `clang-format` (`.clang-format` in root)
- Build system: CMake, no raw Makefiles in `tools/cpp/`

---

## Behavioral Principles (apply to all agents)

### Think Before Acting
- Read the target file fully before modifying it. Understand its callers and callees.
- State your plan before executing: what you will change, why, and what the expected outcome is.
- Never edit code you have not read. Never guess at a file's structure.

### Verify Your Work
- After any code change, run the relevant test suite before reporting done.
- After any refactor, confirm the public API is unchanged (`git diff` should show no signature changes).
- Before marking a task complete: tests pass, lint passes, `git diff` shows no unintended side effects.

### Cost Awareness
- Prefer `Grep`/`Glob` over spawning a sub-agent. Prefer local information over web fetches.
- Only use `WebFetch`/`WebSearch` when local knowledge is genuinely insufficient.
- Only spawn a sub-agent when the task requires language-specific expertise you lack.
- Use one targeted search before broadening — stop early when you have enough information.

### Output Quality
- Cite `file:line` when referencing code. Use tables and code blocks for scan/audit results.
- Keep explanations proportional to complexity — one sentence for a trivial fix, structured breakdown for a complex system.
- When reporting findings (research, debug, audit), indicate confidence: **HIGH** (verified), **MEDIUM** (reasoned), **LOW** (uncertain — needs user review).

### Escalation
Ask the user before:
- Making a breaking API change (signature, return type, behavior contract)
- Deleting files or branches
- Modifying more than 5 files in a single operation
- Taking any action where your confidence in the correct approach is LOW

Decide autonomously for:
- Clear bug fixes with an obvious root cause
- Formatting and lint fixes
- Documentation updates
- Adding tests for existing behavior

### Completeness Checks
Before reporting a task complete, verify all four:
1. Tests pass (run the appropriate test command)
2. Lint is clean (ruff / go vet / clang-format --dry-run)
3. `git diff` shows no unintended modifications
4. The original problem is actually resolved (re-read the request)

---

## Hard Rules (apply to all agents)

- Never modify files outside the agent's designated scope without explicit instruction
- Never run destructive commands (`rm -rf`, `DROP TABLE`, `kill -9`) without confirmation
- Never commit secrets, tokens, or credentials
- Never bypass `.claude/settings.json` deny rules
- Always run tests before marking a task complete
