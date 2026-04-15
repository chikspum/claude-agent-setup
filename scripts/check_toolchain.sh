#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

version_ge() {
  local actual="$1"
  local minimum="$2"
  [[ "$(printf '%s\n%s\n' "$minimum" "$actual" | sort -V | head -n1)" == "$minimum" ]]
}

check_tool_version() {
  local tool="$1"
  local minimum="$2"
  local version="$3"

  if version_ge "$version" "$minimum"; then
    ok "${tool} ${version} (>= ${minimum})"
  else
    fail "${tool} ${version} is below required version ${minimum}"
  fi
}

section "Strict toolchain"

if require_tool python3 "required for repository scripts"; then
  check_tool_version "python3" "3.11" "$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
fi

if require_tool uv "required for Python dependency sync and hermetic pytest/ruff runs"; then
  check_tool_version "uv" "0.4" "$(uv --version | awk '{print $2}')"
fi

if require_tool go "required for tools/go build, test, and lint"; then
  check_tool_version "go" "1.22" "$(go version | awk '{print $3}' | sed 's/^go//')"
fi

if require_tool g++ "required for C++ fallback checks and CI builds"; then
  ok "g++ $(g++ --version | head -n1)"
fi

if require_tool cmake "required for strict C++ build and test verification"; then
  check_tool_version "cmake" "3.22" "$(cmake --version | head -n1 | awk '{print $3}')"
fi

if require_tool ctest "required for strict C++ test verification"; then
  check_tool_version "ctest" "3.22" "$(ctest --version | head -n1 | awk '{print $3}')"
fi

if require_tool clang-format "required for strict C++ lint verification"; then
  check_tool_version "clang-format" "14" "$(clang-format --version | grep -oE '[0-9]+(\.[0-9]+)+' | head -n1)"
fi

finish
