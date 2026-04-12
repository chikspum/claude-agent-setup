# Test Matrix

Track the intended validation surface by area.

## Current Baseline

- Python scaffold: `pytest` in `tools/python/`
- Go scaffold: `go test ./...` in `tools/go/`
- C++ scaffold: `cmake` + `ctest` in `tools/cpp/`

## Use

Expand this file when the repository grows:

- map subsystems to required checks
- record known gaps
- distinguish mandatory checks from optional checks

## Validation Profiles

The authoritative machine-readable mapping lives in [config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml).

Use this file to explain the reasoning behind those profiles in prose when the matrix becomes more complex.
