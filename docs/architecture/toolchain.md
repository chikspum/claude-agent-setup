# Toolchain

Operational toolchain reference for repo-local validation.

## Primary Commands

Agent-friendly repo-local entrypoints:

- `bash scripts/build.sh`
- `bash scripts/test.sh`
- `bash scripts/lint.sh`

Strict wrapper, if `make` is installed:

- `make build`
- `make test`
- `make lint`
- `make doctor`
- `make policy-check`
- `make verify`

Language-specific:

- Python: `cd tools/python && pytest -v`
- Go: `cd tools/go && go test ./... -v`
- C++: `cd tools/cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel && ctest --test-dir build --output-on-failure`

## Expectations

- every documented command should either work or clearly document missing prerequisites
- repo-local scripts should prefer useful fallback checks over opaque shell failures
- strict wrappers should fail when required primary tooling is unavailable
- if a tool is missing in the environment, report it explicitly in validation artifacts
- build/test/lint commands are part of the product surface for agent workflows, not optional maintenance trivia

## Strict Toolchain

Strict verification expects these primary tools:

- `python3 >= 3.11`
- `uv >= 0.4`
- `go >= 1.22`
- `g++`
- `cmake >= 3.22`
- `ctest >= 3.22`
- `clang-format >= 14`

Use `make doctor` to verify the toolchain and `make verify` for the full strict gate.

## Degraded Mode

Repo-local scripts still provide degraded-mode fallbacks for local agent work when strict tooling is unavailable.
Production acceptance should use `make verify`, not degraded-mode output.
