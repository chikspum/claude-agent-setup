# /security-scan

Deep security scan of the entire codebase.

Scan for:

## 1. Hardcoded secrets
Search all files for patterns:
- API keys: `api[_-]?key`, `apikey`
- Tokens: `token\s*[:=]`, `bearer\s+`, `ghp_`, `gho_`, `sk-`, `AKIA`
- Passwords: `password\s*[:=]`, `passwd`, `pwd\s*[:=]`
- Private keys: `BEGIN.*PRIVATE KEY`
- Connection strings: `postgres://`, `mysql://`, `mongodb://`, `redis://` (with credentials)

**Exclude:** `.env.example`, `.env.sample`, `*_test.*`, `*.md`

## 2. Dangerous patterns
- `eval()`, `exec()` with user input (Python)
- `os.system()`, `subprocess.call(shell=True)` (Python)
- `unsafe.Pointer` without justification (Go)
- SQL string concatenation instead of parameterized queries
- `innerHTML` or `dangerouslySetInnerHTML` without sanitization
- `system()`, `popen()` with unvalidated input (C++)

## 3. Dependency vulnerabilities
- Python: check for known vulnerable packages in `pyproject.toml`
- Go: run `go list -m -json all` and flag any with known CVEs if possible

## 4. File permissions
- Check for files with overly permissive modes (777, 666)
- Check for `.env` files accidentally tracked in git

Output as severity-grouped report: CRITICAL / HIGH / MEDIUM / LOW.
