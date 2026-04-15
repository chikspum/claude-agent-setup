#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

section "Python build"
if require_tool uv "required for dependency sync in tools/python"; then
  run_shell "uv sync --extra dev" "$ROOT_DIR/tools/python" "uv sync --extra dev"
else
  run_shell "python syntax smoke check" "$ROOT_DIR/tools/python" "python3 -m py_compile skills.py test_skills.py"
fi

section "Go build"
if require_tool go "required for tools/go builds"; then
  run_shell "go build ./..." "$ROOT_DIR/tools/go" "go build ./..."
fi

section "C++ build"
mkdir -p "$ROOT_DIR/tools/cpp/build"
if require_tool cmake "preferred C++ build entrypoint"; then
  run_shell "cmake configure" "$ROOT_DIR/tools/cpp" "cmake -B build -DCMAKE_BUILD_TYPE=Release"
  run_shell "cmake build" "$ROOT_DIR/tools/cpp" "cmake --build build --parallel"
elif require_tool g++ "fallback compiler for tools/cpp"; then
  run_shell "g++ fallback build" "$ROOT_DIR/tools/cpp" "g++ -std=c++17 tools.cpp tools_test.cpp -o build/tools_test"
fi

finish
