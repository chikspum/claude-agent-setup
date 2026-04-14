# Environment Setup

Environment notes for productive hybrid-agent execution.

## Minimum Local Requirements

- Python 3.11+
- Go 1.22+
- C++17 toolchain
- `pytest`
- `go`
- `cmake`
- `ctest`
- `ruff`
- `clang-format`

## Verification Commands

- `make doctor` — verifies the toolchain (checks that required tools are present and at the expected versions)
- `make verify` — strict full gate; runs all checks and must pass before a change is considered shippable

## Policy

- if a required tool is missing, record that as an environment issue
- do not mark checks as passed when they were skipped
- treat broken local tooling as a throughput problem, not as an acceptable permanent state

## Production Notes

- use Codex runtime profiles that make sandbox and approval mode explicit
- mirror any repo restriction policy in the outer launcher or sandbox when hard guarantees are required
- do not rely on repo markdown policy alone for secrets or destructive command protection
