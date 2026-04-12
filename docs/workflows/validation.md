# Validation

Validation rules for accepting Claude Code output.

## Minimum Validation

Codex should check:

1. `git status --short`
2. `git diff --stat`
3. `git diff`
4. task-specific tests
5. task-specific lint/build commands
6. whether changed files match scope

Preferred repo-local command surface:

- `bash scripts/build.sh`
- `bash scripts/test.sh`
- `bash scripts/lint.sh`

If strict validation is needed and `make` is present, use `make build`, `make test`, and `make lint`.

## Required Outcomes

- changed files are in scope
- required commands ran or were explicitly skipped
- any missing tool or environment dependency is reported
- any degraded fallback path is reported explicitly
- docs do not overclaim behavior the code does not implement

## Artifact Pattern

For non-trivial tasks, keep a validation note with:

- task id
- plan file
- changed files
- commands run
- pass/fail state
- skipped checks and reasons
- Codex acceptance decision

Use:

- [references/codex-validation-checklist.md](/home/ubuntu/claude-agent-setup/docs/references/codex-validation-checklist.md)
- [../../config/validation.yaml](/home/ubuntu/claude-agent-setup/config/validation.yaml) as the machine-readable policy
- [../../artifacts/validations/TEMPLATE.md](/home/ubuntu/claude-agent-setup/artifacts/validations/TEMPLATE.md) as the validation artifact template

## Profile Selection

Choose the validation profile based on the changed area:

- `docs_only`
- `python`
- `go`
- `cpp`
- `mixed`

If more than one profile applies, use the stricter combined set of required checks.
