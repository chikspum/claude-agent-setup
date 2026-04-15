# /hybrid-doc $ARGUMENTS

Hybrid documentation workflow for Claude Code operating under Codex supervision.

`$ARGUMENTS` should be a target file, directory, or module path.

## Goal

Run documentation work in a way that is easy for Codex to validate.

## Steps

1. Resolve the target.
2. Run `/doc $ARGUMENTS`.
3. After `/doc` work is complete, re-read the changed documentation files.
4. Check for:
   - claims about files or functions that do not exist
   - stale references to paths that do not exist
   - workflow statements that are stronger than the current code/tooling supports
5. If a claim is not grounded in the repository, correct it before reporting done.
6. If the work is tied to a plan, mention the plan path and the validation artifact Codex should update.
7. Report the exact files changed and the assumptions Codex should validate.

## Output Format

```markdown
## Documentation Target
- <target>
- <plan path if applicable>

## Files Changed
- <path>

## What Was Updated
- inline docs / DOC.md / workflow docs / references

## Validation Notes For Codex
- <what should be re-read>
- <any environment or code assumptions>
- <validation artifact or run log path if applicable>
```
