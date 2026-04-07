# /deps

Dependency health check — audits all language-specific dependencies for outdated versions and known vulnerabilities.

Runs checks for every language present in the project. Does not stop on failures — runs all checks and reports everything.

## Steps

### 1. Python (if `tools/python/` or `pyproject.toml` exists)
```bash
# List outdated packages
uv pip list --outdated 2>/dev/null || pip list --outdated

# Vulnerability audit
pip audit 2>/dev/null || echo "pip-audit not installed — skipping vuln check"
```

### 2. Go (if `tools/go/go.mod` exists)
```bash
# List available updates
go list -m -u all 2>/dev/null

# Vulnerability check
govulncheck ./... 2>/dev/null || echo "govulncheck not installed — skipping vuln check"
```

### 3. C++ (if `tools/cpp/CMakeLists.txt` exists)
- Read `CMakeLists.txt` and list all `FetchContent_Declare` and `find_package` dependencies
- C++ has no automated update tool — output a manual review note per dependency with its pinned version/tag

### 4. Report

For each language, output a table:

```
## Python Dependencies
| Package | Current | Latest | Vulnerability |
|---------|---------|--------|---------------|
| ...     | ...     | ...    | NONE / CVE-xxx |

## Go Dependencies
| Module | Current | Latest | Vulnerability |
|--------|---------|--------|---------------|
| ...    | ...     | ...    | NONE / CVE-xxx |

## C++ Dependencies (manual review required)
| Library | Pinned Version | Notes |
|---------|----------------|-------|
| ...     | ...            | Check release notes at [url] |

## Recommended Actions
1. [SECURITY] Upgrade X from Y to Z — CVE-xxx
2. [UPDATE] Upgrade A from B to C — minor update available
3. [INFO] D is 2 major versions behind — review changelog before upgrading
```

## Rules

- Always run security fixes first (CVEs before feature updates)
- If a tool is not installed, skip that check gracefully and note it — do not fail the whole command
- Do not automatically apply updates — report what needs attention and let the user decide
- If no issues are found, say so explicitly: "All dependencies up to date. No known vulnerabilities."
