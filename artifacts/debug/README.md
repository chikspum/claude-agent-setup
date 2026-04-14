# Bridge Debug Artifacts

This directory holds machine-readable debug artifacts for abnormal Claude bridge runs.

Current use:
- edit-capable runs that time out or exit abnormally
- post-run classification into `success`, `partial_success`, or `failure`
- captured stdout/stderr tails, changed-file summaries, diff stats, and validation results

These artifacts are operational debugging records.
They are not the acceptance record; validation artifacts under `artifacts/validations/` remain the Codex acceptance surface.
