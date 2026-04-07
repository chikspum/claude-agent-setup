# /todo

TODO/FIXME finder — scans the entire codebase for annotation comments, groups them by severity, and outputs a prioritized table.

Steps:
1. **Search for all annotation patterns** across all source files:
   ```
   grep -rn --include="*.py" --include="*.go" --include="*.cpp" --include="*.h" \
     --include="*.hpp" --include="*.ts" --include="*.js" --include="*.md" \
     -E "TODO|FIXME|HACK|XXX|WARN|OPTIMIZE|BUG" .
   ```
   Exclude: `.git/`, `vendor/`, `node_modules/`, `build/`, `dist/`, `*.min.js`

2. **For each match, capture:**
   - File path and line number
   - The annotation keyword
   - The full comment text
   - The assignee if mentioned (e.g., `TODO(alice):`, `FIXME @bob`)
   - 1 line of context before and after the comment

3. **Classify by severity:**

   | Tier | Keywords | Meaning |
   |------|----------|---------|
   | URGENT | `FIXME`, `BUG`, `XXX` | Broken or incorrect behavior — fix before merging |
   | DEBT | `HACK`, `OPTIMIZE` | Working but problematic — schedule for cleanup |
   | ENHANCEMENT | `TODO` | Planned improvement — track in backlog |
   | INFO | `WARN`, `NOTE` | Awareness only — no action required |

4. **Output a prioritized table**, grouped by tier, sorted by file within each tier:

   ```
   ## URGENT — Fix before merging (N items)

   | File | Line | Assignee | Comment |
   |------|------|----------|---------|
   | tools/go/client.go | 42 | @alice | FIXME: retry logic breaks on timeout |
   | tools/python/parser.py | 87 | — | BUG: doesn't handle empty input |

   ## DEBT — Tech debt to schedule (N items)
   ...

   ## ENHANCEMENT — Backlog items (N items)
   ...

   ## INFO — Notes only (N items)
   ...

   ---
   Total: N items across N files
   ```

5. If there are more than 20 items in any tier, show the top 20 sorted by file path and note the total count.

6. If no annotations are found, say so and suggest the codebase is clean — or that the team uses a different tracking system.
