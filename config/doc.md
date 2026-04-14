# Policy And Machine Config

## About
`config/` contains machine-readable policy used by the hybrid workflow, especially validation rules and agent registry information.

## Read This When
- You are changing validation policy or agent definitions.
- You need to understand what the scripts and docs treat as the machine-enforced contract.
- You are aligning repo behavior with CI or production-readiness checks.

## Related Docs
- `../doc.md`
- `../docs/doc.md`
- `../scripts/doc.md`

## Key Files
- `validation.yaml` - validation policy consumed by repo workflows.
- `agents.yaml` - agent registry or ownership metadata used by the repository.

## Invariants
- Machine-readable policy should agree with the human-readable workflow docs.
- Config changes must be reflected in the scripts or docs that claim to enforce them.
- Do not add policy that the repository cannot realistically validate or report.

## Workflow
- Read `validation.yaml` before changing verification behavior.
- Follow into `docs/references/` and `docs/workflows/` when the change affects operator guidance.
- Check the bridge and verification scripts if the config is meant to change runtime behavior.

## Verification
- Re-run the nearest policy or verification script after config changes.
- If a config change affects acceptance or restrictions, review both human and machine policy surfaces.

## Body
This directory is small but high leverage. Most mistakes here are not syntax errors; they are policy mismatches where config says one thing and the scripts or docs enforce something else. Always trace the config change through to its operational consumer.
