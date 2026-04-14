## Purpose

`cctest/` is the scratch area for Claude Code test runs and short-lived probes.

Use this directory for:
- isolated test inputs and outputs
- temporary fixtures created during workflow validation
- experiments that should not pollute the main repository tree

Do not treat `cctest/` as a product source directory.
Promote anything permanent into the proper repo location after Codex validation.
