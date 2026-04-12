#!/usr/bin/env bash

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT="${STRICT:-0}"
FAILURES=0
DEGRADED=0

section() {
  printf '\n== %s ==\n' "$1"
}

ok() {
  printf '[ok] %s\n' "$1"
}

warn() {
  printf '[warn] %s\n' "$1"
}

fail() {
  printf '[fail] %s\n' "$1"
  FAILURES=$((FAILURES + 1))
}

note_missing() {
  local tool="$1"
  local reason="$2"
  warn "missing tool: ${tool} (${reason})"
  DEGRADED=1
  if [[ "$STRICT" == "1" ]]; then
    FAILURES=$((FAILURES + 1))
  fi
}

require_tool() {
  local tool="$1"
  local reason="$2"
  if command -v "$tool" >/dev/null 2>&1; then
    return 0
  fi
  note_missing "$tool" "$reason"
  return 1
}

run_cmd() {
  local label="$1"
  shift
  if "$@"; then
    ok "$label"
  else
    fail "$label"
  fi
}

run_shell() {
  local label="$1"
  local workdir="$2"
  local command="$3"
  if (cd "$workdir" && bash -lc "$command"); then
    ok "$label"
  else
    fail "$label"
  fi
}

finish() {
  printf '\n== Summary ==\n'
  if [[ "$DEGRADED" == "1" ]]; then
    warn "degraded mode was used; see missing-tool messages above"
  fi

  if [[ "$FAILURES" -gt 0 ]]; then
    fail "completed with ${FAILURES} failing step(s)"
    exit 1
  fi

  ok "completed successfully"
}
