#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

section "Python lint"
if command -v uv >/dev/null 2>&1; then
  run_shell "uv run --extra dev ruff check ." "$ROOT_DIR/tools/python" "uv run --extra dev ruff check ."
  run_shell "uv run --extra dev ruff format --check ." "$ROOT_DIR/tools/python" "uv run --extra dev ruff format --check ."
elif require_tool ruff "preferred Python lint and format checker"; then
  run_shell "ruff check ." "$ROOT_DIR/tools/python" "ruff check ."
  run_shell "ruff format --check ." "$ROOT_DIR/tools/python" "ruff format --check ."
else
  run_shell "python syntax smoke check" "$ROOT_DIR/tools/python" "python3 -m py_compile skills.py test_skills.py"
fi

section "Go lint"
if require_tool go "required for go vet"; then
  run_shell "go vet ./..." "$ROOT_DIR/tools/go" "go vet ./..."
fi
if command -v gofmt >/dev/null 2>&1; then
  run_shell "gofmt -l . is empty" "$ROOT_DIR/tools/go" "test -z \"$(gofmt -l .)\""
else
  note_missing gofmt "preferred Go formatter check"
fi

section "C++ lint"
if require_tool clang-format "preferred C++ format checker"; then
  run_shell "clang-format --dry-run -Werror" "$ROOT_DIR/tools/cpp" "clang-format --dry-run -Werror *.cpp *.h"
elif require_tool g++ "fallback compiler warnings check for tools/cpp"; then
  run_shell "g++ warnings check" "$ROOT_DIR/tools/cpp" "g++ -std=c++17 -Wall -Wextra -Wpedantic -fsyntax-only tools.cpp tools_test.cpp"
fi

finish
