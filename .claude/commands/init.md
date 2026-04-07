# /init $ARGUMENTS

Scaffold a new tool component following the project's existing patterns.

`$ARGUMENTS` format: `<language> <name>` — e.g., `python word_counter`, `go file_watcher`, `cpp image_compress`

## Routing

`/init` always delegates to the language agent that owns the target directory:

- `python` → delegate to **python-agent** (owns `tools/python/`)
- `go` → delegate to **go-agent** (owns `tools/go/`)
- `cpp` → delegate to **cpp-agent** (owns `tools/cpp/`)

The language agent follows the steps below. The orchestrator does not scaffold files directly.

---

## Steps

### 1. Validate input
- Parse language (`python` / `go` / `cpp`) and name from `$ARGUMENTS`
- If either is missing or invalid, stop and ask: "Usage: /init <python|go|cpp> <tool_name>"
- Convert name to the correct casing: `snake_case` for Python, `snake_case` for Go files, `snake_case` for C++ files
- Check for duplicates: if `tools/<language>/<name>` already exists, stop and report

### 2. Read an existing tool for pattern reference
Before generating anything, read one existing tool in the target language to match its structure exactly:
- Python: read `tools/python/skills.py`
- Go: read `tools/go/tools.go`
- C++: read `tools/cpp/tools.cpp` and `tools/cpp/tools.h`

### 3. Generate files

**Python** → creates 2 files:
- `tools/python/<name>.py` — uses `SkillInput` / `SkillOutput` pattern from `skills.py`
- `tools/python/test_<name>.py` — `pytest` test with at least one happy-path and one edge-case test

**Go** → creates 2 files inside a new subdirectory:
- `tools/go/<name>/<name>.go` — package `<name>`, imports shared types from the root module (`tools "github.com/your-org/claude-agent-setup/tools/go"`), exports `Run(ctx context.Context, args tools.Args) (tools.Result, error)`
- `tools/go/<name>/<name>_test.go` — `go test` file with table-driven tests, package `<name>_test`

**C++** → creates 3 things:
- `tools/cpp/<name>.h` — public header with `extern "C"` FFI declaration
- `tools/cpp/<name>.cpp` — implementation
- Update `tools/cpp/CMakeLists.txt` — add the new `.cpp` to the existing `add_library` or `add_executable` target

### 4. Build and test
After creating the files:
- Python: `cd tools/python && uv run pytest test_<name>.py -v`
- Go: `cd tools/go && go build ./... && go test ./<name>/... -v`
- C++: `cd tools/cpp && cmake --build build && ctest --test-dir build -R <name>`

If build or tests fail, fix the generated code before reporting done. Do not leave a scaffolded component that does not compile.

### 5. Report

```
## Created: <language>/<name>

Files:
- tools/<language>/<name>/<name>.<ext>       — [one-line description of what it does]
- tools/<language>/<name>/<name>_test.<ext>  — [N tests: what they cover]

Build: PASS
Tests: N/N passed

Next steps:
- Replace the stub implementation in <name>.<ext> with real logic
- Add more test cases as the implementation grows
```

## Rules

- Never overwrite an existing file — check first, stop if duplicate
- Always build and test after scaffolding — a scaffold that does not compile is worse than no scaffold
- Match the exact patterns from existing tools — do not invent new patterns
- The stub implementation should be minimal but valid (compiles, tests pass against stub behavior)
