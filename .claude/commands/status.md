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
# Python — syntax check (no build step needed)
python -m py_compile tools/python/skills.py 2>&1 | head -5 || echo "PASS"

# Go
cd tools/go && go build ./... 2>&1 | head -10

# C++
cd tools/cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -3 && cmake --build build 2>&1 | tail -5
```

### 3. Tests
```bash
# Python
cd tools/python && uv run pytest --tb=no -q 2>&1 | tail -5

# Go
cd tools/go && go test ./... 2>&1 | tail -5

# C++
cd tools/cpp && ctest --test-dir build --output-on-failure 2>&1 | tail -5
```

### 4. Lint
```bash
# Python
cd tools/python && ruff check . 2>&1 | tail -5

# Go
cd tools/go && go vet ./... 2>&1 | tail -5

# C++
find tools/cpp -name '*.cpp' -o -name '*.h' | xargs clang-format --dry-run --Werror 2>&1 | head -10
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
| Language | Status |
|----------|--------|
| Python   | PASS   |
| Go       | PASS   |
| C++      | FAIL   |

### Tests
| Language | Passed | Failed | Skipped |
|----------|--------|--------|---------|
| Python   | 12     | 0      | 1       |
| Go       | 8      | 0      | 0       |
| C++      | 5      | 2      | 0       |

### Lint
| Language | Status         |
|----------|----------------|
| Python   | PASS           |
| Go       | PASS           |
| C++      | 3 issues       |

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
- If a tool is not installed, skip that check and note it
