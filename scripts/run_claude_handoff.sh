#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <plan-path> [additional run_claude_from_plan.py args]" >&2
  exit 1
fi

PLAN_PATH="$1"
shift

exec python3 "$ROOT_DIR/scripts/run_claude_from_plan.py" "$PLAN_PATH" "$@"
