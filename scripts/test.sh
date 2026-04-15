#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

section "Python tests"
if command -v uv >/dev/null 2>&1; then
  run_shell "uv run --extra dev pytest -q" "$ROOT_DIR/tools/python" "uv run --extra dev pytest -q"
elif require_tool pytest "required for tools/python tests when uv is unavailable"; then
  run_shell "pytest -q" "$ROOT_DIR/tools/python" "pytest -q"
fi

section "Go tests"
if require_tool go "required for tools/go tests"; then
  run_shell "go test ./..." "$ROOT_DIR/tools/go" "go test ./..."
fi

section "C++ tests"
mkdir -p "$ROOT_DIR/tools/cpp/build"
if command -v cmake >/dev/null 2>&1 && command -v ctest >/dev/null 2>&1; then
  run_shell "cmake configure" "$ROOT_DIR/tools/cpp" "cmake -B build -DCMAKE_BUILD_TYPE=Release"
  run_shell "cmake build" "$ROOT_DIR/tools/cpp" "cmake --build build --parallel"
  run_shell "ctest --output-on-failure" "$ROOT_DIR/tools/cpp" "ctest --test-dir build --output-on-failure"
else
  if ! command -v cmake >/dev/null 2>&1; then
    note_missing cmake "preferred C++ test configure path"
  fi
  if ! command -v ctest >/dev/null 2>&1; then
    note_missing ctest "preferred C++ test runner"
  fi
  if require_tool g++ "fallback compiler for tools/cpp tests"; then
    run_shell "g++ fallback test build" "$ROOT_DIR/tools/cpp" "g++ -std=c++17 tools.cpp tools_test.cpp -o /tmp/claude-agent-tools-test-$$"
    run_shell "fallback test binary" "$ROOT_DIR/tools/cpp" "/tmp/claude-agent-tools-test-$$"
    run_shell "cleanup fallback test binary" "$ROOT_DIR/tools/cpp" "rm -f /tmp/claude-agent-tools-test-$$"
  fi
fi

finish
