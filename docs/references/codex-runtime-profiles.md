# Codex Runtime Profiles

Runtime profiles define the Codex CLI defaults that are actually supported by Codex itself.

## Recommended Profiles

### `safe`

- sandbox: `workspace-write`
- approval mode: `on-request`
- intended use: default internal-team work

### `full-access`

- sandbox: `danger-full-access`
- approval mode: `on-request`
- intended use: broader repository work when the task still follows repo restriction policy

## Rule

Keep Codex runtime profiles limited to settings Codex CLI actually understands.
Do not invent unsupported denylist semantics in `config.toml`.

## Policy Split

- runtime defaults belong in Codex config
- forbidden paths and commands belong in repo policy and launcher enforcement
- hard restrictions should be mirrored by the outer sandbox or launcher
