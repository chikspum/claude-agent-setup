# Restriction Policy

Production restriction policy for the internal-team operating mode.

## Documented Policy Baseline

These are the minimum restrictions that should appear in any production launcher profile for this repo.

## Baseline Forbidden Paths

- `secrets/`
- `.ssh/`
- `.env`
- `*.pem`
- `*.key`

## Baseline Forbidden Commands

- `git reset --hard`
- `ssh`

## Current Claude Runtime Enforcement

The checked-in Claude runtime profile is stricter than the baseline policy above.
See [/.claude/settings.json](/home/ubuntu/claude-agent-setup/.claude/settings.json) for the current enforced deny-list and hooks.

Current runtime enforcement also blocks or guards:

- secret and credential reads beyond `.env`, including credential- and token-shaped files
- secret writes outside sample and example files
- `sudo`, `dd`, `mkfs`, and `chmod 777`
- `curl | bash`, `curl | sh`, `wget | bash`, and `wget | sh`
- `git push --force` and `git push -f`
- leaked-token or private-key output in Bash tool results

## Rule Semantics

- if a task touches a forbidden path, stop and report the restriction
- if a task requires a forbidden command, stop and report the restriction
- do not work around the restriction implicitly
- enforce critical restrictions both in repo policy and in the launcher/sandbox when possible

## Production Expectation

Repo policy documents the rules.
Launcher or sandbox configuration must provide the hard guarantee for high-risk restrictions.
