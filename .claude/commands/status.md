# /status

Project health dashboard — one-command overview of git state, build, tests, lint, and open issues.

Runs ALL checks even if some fail. Never stop early.

## Steps

### 1. Git state
```bash
git branch --show-current
git status --short
git log --oneline -1
git rev-list --count --left-right @{upstream}...HEAD 2>/dev/null || echo "no upstream"
```

### 2. Build status
```bash
bash scripts/build.sh
```

### 3. Tests
```bash
bash scripts/test.sh
```

### 4. Lint
```bash
bash scripts/lint.sh
```

### 5. Open issues
```bash
grep -rn 'TODO\|FIXME\|HACK\|BUG' tools/ --include='*.py' --include='*.go' --include='*.cpp' --include='*.h' | wc -l
```

## Output Format

```
## Project Status — [branch name]

### Git
| Item           | Value                          |
|----------------|--------------------------------|
| Branch         | main                           |
| Uncommitted    | 3 files changed                |
| Last commit    | abc1234 — message              |
| Ahead/behind   | ↑2 ↓0 vs origin/main           |

### Build
| Surface                  | Status |
|--------------------------|--------|
| `bash scripts/build.sh`  | PASS / FAIL / PASS (degraded mode) |

### Tests
| Surface                 | Status |
|-------------------------|--------|
| `bash scripts/test.sh`  | PASS / FAIL / PASS (degraded mode) |

### Lint
| Surface                 | Status |
|-------------------------|--------|
| `bash scripts/lint.sh`  | PASS / FAIL / PASS (degraded mode) |

### Environment Gaps
| Tool | Effect |
|------|--------|
| `uv` | Python build uses fallback checks |
| `cmake` / `ctest` | C++ build and tests use fallback compiler flow |
| `ruff` / `clang-format` | lint uses fallback checks |

### Open Issues
| Type  | Count |
|-------|-------|
| TODO  | 7     |
| FIXME | 2     |
| HACK  | 1     |
| BUG   | 0     |

### Summary
[One sentence: overall health and the most important thing needing attention]
```

## Rules

- Run ALL steps even if build fails — a failing build does not mean tests or lint checks should be skipped
- If a language has no source files yet, skip it and note "no source files"
- If a tool is not installed, record the missing tool and whether the repo scripts fell back or had to skip work entirely
- Distinguish `PASS` from `PASS (degraded mode)` whenever fallback validation was used
