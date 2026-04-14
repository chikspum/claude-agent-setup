# Artifacts And Execution Records

## About
`artifacts/` stores plans-adjacent operational output: run logs, validation records, metrics summaries, and bridge debug artifacts.

## Read This When
- You are validating whether a delegated run was accepted, partial, or blocked.
- You need to inspect the machine-readable evidence of a bridge timeout or abnormal run.
- You are changing artifact policy, naming, or lifecycle.

## Related Docs
- `../doc.md`
- `../docs/doc.md`
- `../scripts/doc.md`
- `../config/doc.md`

## Key Files
- `runs/README.md` - run-log expectations.
- `runs/TEMPLATE.md` - run-log template.
- `validations/TEMPLATE.md` - validation artifact template.
- `metrics/summary.json` - machine-readable operational snapshot.
- `debug/` - bridge timeout and abnormal-run debug payloads.

## Invariants
- Non-trivial work should leave enough artifact evidence for another agent to reconstruct what happened.
- Validation artifacts represent Codex review state, not Claude self-acceptance.
- Debug artifacts should be machine-readable and focused on recovery, not narrative.

## Workflow
- Read run logs when you need what Claude was asked to do and how it ended.
- Read validation artifacts when you need Codex acceptance state.
- Read debug artifacts when a bridge run timed out or ended abnormally.
- Regenerate or check metrics only when the operational summary is supposed to move.

## Verification
- Artifact policy changes should be checked against the generating scripts and templates.
- If you change bridge debug payloads, update focused tests and the relevant workflow/reference docs.

## Body
The repository uses artifacts as continuity, not just audit logs. Another agent should be able to open a run log, validation file, or debug payload and understand the task, observed outcome, and next recovery step without replaying the entire conversation.
