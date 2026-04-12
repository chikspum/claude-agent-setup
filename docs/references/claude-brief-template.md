# Claude Brief Template

```text
You are working in /home/ubuntu/claude-agent-setup.

Goal:
- [clear outcome]

Required changes:
- [path]: [exact change]

Forbidden changes:
- [path or category]

Constraints:
- do not modify unrelated files
- do not change public interfaces unless explicitly requested

Use repository commands when helpful:
- /doc for documentation work
- /test for repo-native checks
- /commit only after Codex validation
- /pr only after Codex validation

Recommended CLI invocation:
- provide the brief to `claude -p` via stdin
- use `--add-dir /home/ubuntu/claude-agent-setup`
- prefer `--permission-mode acceptEdits` for bounded edit tasks

Verification:
- run [command]
- run [command]

Final response:
- files changed
- tests and checks run
- skipped checks and why
- residual issues
```
