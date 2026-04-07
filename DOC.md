# claude-agent-setup — Project Documentation

A multi-language agent toolkit for Claude Code. Provides structured agent roles, reusable tool scaffolds, a slash-command library, and a behavioral framework that teaches agents *how to think*, not just what tools to use.

---

## Table of Contents

1. [What This Is](#what-this-is)
2. [Architecture](#architecture)
3. [Agent Roles](#agent-roles)
4. [Slash Commands](#slash-commands)
5. [Permissions Model](#permissions-model)
6. [Behavioral Principles](#behavioral-principles)
7. [Directory Reference](#directory-reference)
8. [Quickstart](#quickstart)
9. [Extending the Toolkit](#extending-the-toolkit)

---

## What This Is

`claude-agent-setup` is a **template project** for working with Claude agents across three languages: Python, Go, and C++. It solves a common problem — agents that know *what* commands exist but not *when* to use them, *how* to verify their work, or *when* to stop and ask.

The toolkit gives you:
- Four agent profiles with clear ownership boundaries and escalation rules
- Sixteen slash commands covering the full dev workflow (build → review → deploy)
- A blocklist-based permission model with secret-leak hooks
- Behavioral principles baked into `CLAUDE.md` that all agents read at startup

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Orchestrator Agent            │  ← coordinates sub-agents
│  (task decomposition, progress reports) │
├──────────┬──────────────┬───────────────┤
│  Python  │      Go      │     C++       │  ← language-specific agents
│  Agent   │    Agent     │    Agent      │
├──────────┴──────────────┴───────────────┤
│              Tool Layer                 │  ← shared tools & skills
│   tools/python/  tools/go/  tools/cpp/  │
└─────────────────────────────────────────┘
         ↑
   .claude/settings.json   ← blocklist permissions + hooks
   .claude/commands/        ← slash commands (16 total)
   agents/*.md              ← agent profiles (read by Claude at spawn)
   config/                  ← machine-readable capability matrix
```

**Key design decisions:**
- Each agent owns its language directory and cannot touch other agents' files
- The orchestrator never touches `tools/` directly — it delegates
- Behavioral rules live in `.md` files (human-readable, agent-readable), not in code
- Permissions are blocklist-based: everything is allowed unless explicitly denied

---

## Agent Roles

### Orchestrator (`agents/orchestrator.md`)
Coordinates the other agents. Classifies tasks into three tiers before acting:

| Tier | When | Action |
|------|------|--------|
| **Simple** | Single-file reads, config edits, CLAUDE.md updates | Do it directly, no delegation |
| **Medium** | Single-language task | Spawn one sub-agent with a clear brief |
| **Complex** | Cross-language or multi-step | Decompose → assign → track progress per step |

Error handling: re-delegates once with error context attached; stops and reports to user after 2 failed attempts.

### Python Agent (`agents/python-agent.md`)
Owns `tools/python/` and all `*.py` files. Stack: Python 3.11+, uv, pytest, ruff.

### Go Agent (`agents/go-agent.md`)
Owns `tools/go/`, `*.go`, `go.mod`, `go.sum`. Stack: Go 1.22+, go test, golangci-lint.

### C++ Agent (`agents/cpp-agent.md`)
Owns `tools/cpp/`, `*.cpp`, `*.h`, `*.hpp`, `CMakeLists.txt`. Stack: C++17, CMake, clang-format, clang-tidy.

**All sub-agents share the same escalation rules:**
- Ask the user before changing a public API signature
- Escalate to orchestrator for cross-language coordination
- On test failure: verify it's your change that caused it before reporting

---

## Slash Commands

All commands live in `.claude/commands/`. Invoke with `/command-name [args]`.

### Build & Test

| Command | What it does |
|---------|-------------|
| `/build` | Builds all three languages and reports pass/fail per language |
| `/test` | Runs full test suite (pytest / go test / ctest), structured output |
| `/status` | Project health dashboard: git state + build + tests + lint + open TODOs |

### Code Quality

| Command | What it does |
|---------|-------------|
| `/review` | Reviews all uncommitted changes for security, bugs, and quality |
| `/refactor <target>` | Safe refactoring with scope verification — no API changes, tests required |
| `/fix <error>` | Root-cause analysis + minimal targeted fix + test verification |
| `/security-scan` | Deep vulnerability scan: secrets, injection, CVEs, permissions |
| `/audit` | Permission and settings audit — checks `settings.json` and hooks |

### Documentation & Discovery

| Command | What it does |
|---------|-------------|
| `/explain <target>` | Explains how a file, function, or module works |
| `/doc <target>` | Generates or updates inline docs (Google-style / godoc / Doxygen) |
| `/todo` | Finds and prioritizes all TODO/FIXME/HACK/BUG comments |
| `/deps` | Dependency health check: outdated versions + CVE scan per language |
| `/research <topic>` | Structured web research with cost limits and confidence ratings |

### Git & Workflow

| Command | What it does |
|---------|-------------|
| `/commit` | Conventional commit helper with secret guard and confirmation prompt |
| `/pr` | Creates a pull request via `gh` with auto-generated summary and test plan |

### Scaffolding

| Command | What it does |
|---------|-------------|
| `/init <lang> <name>` | Scaffolds a new tool (source + tests) following existing project patterns |

---

## Permissions Model

Access uses a **blocklist model** — everything is allowed by default, specific dangerous operations are denied.

**What is blocked globally** (`.claude/settings.json` deny rules):
- Destructive shell commands: `rm -rf`, `kill -9`, `DROP TABLE`, `format`, `mkfs`
- Writing to secret files: `.env`, `*.pem`, `*.key`, `id_rsa`, credential files

**Runtime hooks:**
- `PreToolUse` — blocks any write to a file matching secret patterns before it happens
- `PostToolUse` — scans tool output for leaked tokens after every tool call (detects `ghp_`, `sk-`, `AKIA`, private key headers)

**Per-agent scoping** is enforced through the `owns` / `cannot_modify` fields in `config/agents.yaml` and the scope rules in each agent's `.md` profile — not through `settings.json` overrides.

See `config/permissions.yaml` for the full documented deny list in human-readable form.

---

## Behavioral Principles

These principles are defined in `CLAUDE.md` and apply to all agents. They answer the question "how should an agent think?" rather than "what can it do?".

**Think Before Acting** — read the target file fully before modifying it; state the plan before executing.

**Verify Your Work** — run tests after every change; confirm public APIs are unchanged after refactors; check `git diff` for unintended side effects before reporting done.

**Cost Awareness** — prefer `Grep`/`Glob` over spawning sub-agents; prefer local knowledge over web fetches; stop early when enough information is collected.

**Output Quality** — cite `file:line` for code references; use tables/code blocks for structured results; indicate confidence level (`HIGH` / `MEDIUM` / `LOW`) when reporting research or debug findings.

**Escalation** — ask the user before breaking API contracts, deleting files, or modifying >5 files. Decide autonomously for clear bug fixes, lint fixes, and doc updates.

**Completeness Checks** — before marking done: tests pass, lint passes, `git diff` is clean, original request is resolved.

---

## Directory Reference

```
claude-agent-setup/
├── DOC.md                     # This file
├── CLAUDE.md                  # Agent startup context (read by all agents)
├── Makefile                   # Top-level: build / test / lint / clean
├── .gitignore
├── .env.example               # Environment variable template
│
├── .claude/
│   ├── settings.json          # Blocklist deny rules + PreToolUse/PostToolUse hooks
│   └── commands/              # 16 slash commands
│       ├── build.md           # /build
│       ├── test.md            # /test
│       ├── status.md          # /status
│       ├── review.md          # /review
│       ├── refactor.md        # /refactor <target>
│       ├── fix.md             # /fix <error>
│       ├── security-scan.md   # /security-scan
│       ├── audit.md           # /audit
│       ├── explain.md         # /explain <target>
│       ├── doc.md             # /doc <target>
│       ├── todo.md            # /todo
│       ├── deps.md            # /deps
│       ├── research.md        # /research <topic>
│       ├── commit.md          # /commit
│       ├── pr.md              # /pr
│       └── init.md            # /init <lang> <name>
│
├── agents/
│   ├── orchestrator.md        # Orchestrator profile (task tiers, error handling, progress reporting)
│   ├── python-agent.md        # Python agent profile (ownership, stack, escalation rules)
│   ├── go-agent.md            # Go agent profile
│   └── cpp-agent.md           # C++ agent profile
│
├── tools/
│   ├── python/
│   │   ├── skills.py          # Skill scaffold (SkillInput/SkillOutput pattern)
│   │   └── test_skills.py     # Pytest tests
│   ├── go/
│   │   ├── tools.go           # Tool scaffold (Run(ctx, Args) pattern)
│   │   └── tools_test.go      # Go tests
│   └── cpp/
│       ├── tools.cpp          # C++ tool scaffold
│       ├── tools.h            # Public header with extern "C" FFI
│       ├── tools_test.cpp     # CTest tests
│       └── CMakeLists.txt     # CMake build config
│
└── config/
    ├── agents.yaml            # Machine-readable capability matrix (owns, stack, web_access)
    └── permissions.yaml       # Human-readable deny-list documentation
```

---

## Quickstart

```bash
# Build all languages
make build

# Run all tests
make test

# Run lint
make lint

# Or use slash commands in Claude Code:
# /status          — see project health at a glance
# /build           — build everything
# /test            — run all tests
# /research <topic> — look something up
```

---

## Extending the Toolkit

### Add a new tool to an existing language
Use `/init <language> <name>` — it reads the existing patterns and scaffolds source + test files that match.

### Add a new slash command
Create `.claude/commands/<name>.md` with:
1. A title line: `# /<name> $ARGUMENTS`
2. A one-line description of what it does
3. Numbered steps
4. An output format section

Then add it to the `commands/` tree in `CLAUDE.md` and `DOC.md`.

### Add a new agent language
1. Create `agents/<lang>-agent.md` — define ownership, stack, and escalation rules
2. Add an entry to `config/agents.yaml` with `owns`, `stack`, and `web_access`
3. Create `tools/<lang>/` with a scaffold tool following the existing patterns
4. Update the orchestrator's delegation table in `agents/orchestrator.md`
5. Update `CLAUDE.md` architecture diagram and agent roles table

### Modify permissions
Edit `.claude/settings.json` (deny rules) or the hook scripts inline.
Document the change in `config/permissions.yaml`.
Run `/audit` after any permission change to verify the model is consistent.
