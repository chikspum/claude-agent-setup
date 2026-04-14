# Claude Slash Commands

## About
`.claude/commands/` contains the Claude Code slash-command prompts used in this repository, including both generic development commands and hybrid Codex-supervised commands.

## Read This When
- You are changing how Claude Code should execute a slash command in this repository.
- You need to understand which commands are generic versus hybrid workflow commands.
- You are debugging why a Codex to Claude handoff used a specific command pattern.

## Related Docs
- `../../doc.md`
- `../../docs/doc.md`
- `../../scripts/doc.md`
- `../../CLAUDE.md`

## Key Files
- `handoff.md` - plan-driven Claude execution entrypoint for hybrid work.
- `hybrid-doc.md`, `hybrid-test.md`, `hybrid-fix.md`, `hybrid-commit.md`, `hybrid-pr.md` - Codex-supervised command variants.
- `build.md`, `review.md`, `test.md`, `status.md`, `commit.md`, `pr.md`, `init.md` - baseline Claude runtime commands.
- `doc.md` - the actual `/doc` slash-command prompt and should not be repurposed as a directory map.

## Invariants
- Slash commands are Claude runtime affordances, not Codex-native commands.
- Hybrid commands should stay aligned with the repository bridge, plan, and validation model.
- Command prompts should stay scoped and operational, not become a second system of record for policy that already lives in `docs/` or config.
- `doc.md` in this directory is a command prompt, so directory-level documentation must live in `DOC.md`.

## Workflow
1. Read `CLAUDE.md` and the nearest workflow/reference doc first.
2. Change the specific command prompt that owns the behavior.
3. Re-check the adjacent hybrid command if the change affects shared handoff semantics.
4. Confirm the prompt still matches the actual scripts and policy surfaces it refers to.

## Verification
- Re-read `docs/references/command-reference.md` and `docs/workflows/hybrid-execution.md` when command semantics change.
- If the command routes through the bridge, validate the corresponding bridge tests and scripts.

## Body
This directory exists so Claude Code has repo-local operational shortcuts. The highest-risk drift here is when a command prompt tells Claude to do something that the scripts, restrictions, or validation flow do not actually support. Keep these prompts thin, scoped, and consistent with the real bridge and policy surfaces.
