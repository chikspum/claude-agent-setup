# /audit

Audit the project for permission and security issues.

Check the following:

1. **settings.json integrity** — verify `.claude/settings.json` deny rules are intact and haven't been weakened
2. **Hardcoded secrets** — search for API keys, tokens, passwords in code:
   - Patterns: `api_key`, `secret`, `password`, `token`, `Bearer `, `sk-`
   - Files: `**/*.py`, `**/*.go`, `**/*.cpp`, `**/*.h`, `**/*.json`, `**/*.yaml`
3. **Dependency licenses** — flag any GPL dependencies if this is a commercial project
4. **Agent scope violations** — check if any agent-owned files were modified outside their scope (use git diff)

Report findings grouped by severity: Critical / Warning / Info.
