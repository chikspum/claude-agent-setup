# /review

Review all uncommitted changes for quality, security, and correctness.

Steps:
1. Run `git diff --staged` and `git diff` to see all changes
2. For each changed file, check:
   - **Security:** hardcoded secrets, SQL injection, command injection, XSS
   - **Bugs:** off-by-one, nil/null dereferences, unchecked errors, race conditions
   - **Quality:** dead code, duplicated logic, unclear naming, missing edge cases
   - **Tests:** do changes have corresponding test updates?
3. Check that no `.env`, credential, or key files are staged: `git diff --staged --name-only | grep -iE '\.env|secret|credential|\.pem|id_rsa'`

Output format:
```
## Security  (block merge if any)
- ...

## Bugs  (block merge if any)
- ...

## Quality  (suggestions)
- ...

## Missing tests
- ...

## Verdict: PASS / NEEDS CHANGES
```

**Self-check before reporting:** run `git diff --name-only` and compare against the files you reviewed above. If you reviewed fewer files than were changed, go back and cover the missed files.
