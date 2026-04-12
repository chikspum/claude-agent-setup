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

## Current Gaps

Known gaps observed on 2026-04-07 in this workspace:

- `make` is missing, so direct `make` entrypoints are not portable as the only documented surface
- `uv`, `ruff`, `cmake`, `ctest`, and `clang-format` may be absent in local environments
- repo-local scripts now provide explicit degraded-mode output, but full validation still depends on the primary tools above
