# Hybrid Agent Maximization Plan

Research-based implementation plan for a hybrid engineering workflow where:

- Codex acts as manager, architect, planner, and validator
- Claude Code acts as implementation-focused developer and workflow executor

This plan is based on current official guidance and reports from OpenAI and Anthropic reviewed on April 7, 2026.

## Executive Summary

The best-performing version of this setup is not "two agents doing the same job."
It is a supervised hierarchical system:

1. Codex plans and constrains the work.
2. Claude Code executes well-scoped changes quickly.
3. Codex validates outputs, controls scope, and decides what is accepted.

This maps cleanly to:

- OpenAI's guidance that agents perform best with strong repository-local instructions, reliable environments, and structured task prompts.
- Anthropic's guidance that Claude Code performs best with concise project memory, reusable slash-command workflows, and explicit permission policy.
- Multi-agent architecture guidance favoring orchestrator + specialist patterns, evaluator-optimizer loops, modular skills, and strong observability.

The main implementation priority is not "more autonomy."
It is better legibility, better task packaging, better verification, and better instrumentation.

---

## Key Best Practices From Research

### 1. Keep the manager and the implementer separate

Recommended operating model:

- Codex owns planning, decomposition, acceptance criteria, and final validation.
- Claude Code owns bounded execution work inside an explicit scope.

Why:

- Anthropic's multi-agent guidance favors centralized orchestration or hybrid supervision when control and quality matter.
- Anthropic's evaluator-optimizer pattern strongly matches our workflow: one system generates, another evaluates against defined criteria.

Implication for this repo:

- Do not let Claude Code decide by itself whether work is complete.
- Do not let Codex drift into doing all implementation directly unless delegation is clearly slower.

### 2. Use short control files and a structured knowledge base

OpenAI's February 11, 2026 Harness engineering writeup explicitly argues against one giant `AGENTS.md`. Their recommendation is:

- a short agent control file as a map
- a structured repository-local docs system as the source of truth
- versioned plans and decision records in-repo

Implication for this repo:

- `CODEX.md`, `CLAUDE.md`, and `AGENTS.md`-style files should remain concise.
- Detailed truth should move into dedicated docs by topic.
- Plans should become first-class repository artifacts.

### 3. Start large changes with planning mode, then switch to execution

OpenAI's "How OpenAI uses Codex" recommends a two-step flow:

- first ask for an implementation plan
- then execute from that plan

It also recommends tasks that are roughly one engineer-hour or a few hundred lines of code, plus prompts that read like well-written GitHub issues.

Implication for this repo:

- Codex should always produce a written execution brief before invoking Claude Code for non-trivial work.
- Claude work items should be intentionally bounded.

### 4. Invest in the environment, not just the prompt

OpenAI explicitly notes that better startup scripts, environment variables, and internet access reduce agent error rates. Anthropic similarly emphasizes project memory, custom skills, and reusable commands.

Implication for this repo:

- Build/test/lint commands must be complete and runnable.
- Missing local tools should be treated as a productivity bug.
- Repeated workflows should be encoded as slash commands or skills.

### 5. Use custom commands and skills aggressively for repeated flows

Anthropic's Claude Code materials consistently emphasize:

- project memory via `CLAUDE.md`
- `/init` for project bootstrap
- custom slash commands and skills for repeatable workflows

Anthropic's internal usage report also highlights extensive use of custom slash commands and documentation generation.

Implication for this repo:

- common hybrid workflows should become explicit skills or project commands
- do not rely on free-form prompting for recurring tasks

### 6. Reduce permission fatigue without removing supervision

Anthropic's March 25, 2026 Claude Code auto mode article warns that `--dangerously-skip-permissions` is unsafe in most situations, while manual approvals create fatigue. Their guidance points toward safer automation, not blind bypass.

Implication for this repo:

- for local trusted execution, Codex may temporarily use broad permissions when post-run validation is guaranteed
- for durable team workflow, prefer explicit project permission policy and safer automation modes over habitual full bypass

### 7. Add observability for agent behavior, not just build results

Anthropic's architecture paper stresses that multi-agent systems need observability into delegation, interaction patterns, and failure causes. OpenAI's Harness engineering also emphasizes versioned plans, quality docs, and repository-local artifacts that agents can inspect directly.

Implication for this repo:

- track what Codex asked Claude Code to do
- track what files changed
- track what validation actually ran
- track where delegation failed, not just that it failed

---

## Target Operating Model

### Codex role

- intake and triage
- architecture decisions
- decomposition into bounded work items
- generation of Claude execution briefs
- diff review
- validation execution
- merge gate
- escalation handling

### Claude Code role

- targeted implementation
- `/doc` runs for documentation updates
- `/review` as a secondary review signal
- `/test` for repo-native test flow
- `/commit` only after Codex validation
- `/pr` only after Codex validation
- `/init` for Claude-side bootstrap when intentionally requested

### Workflow pattern

1. Codex inspects repo locally.
2. Codex writes a plan and acceptance criteria.
3. Codex delegates a bounded task to Claude Code.
4. Claude Code edits and optionally uses repository skills/commands.
5. Codex reviews `git diff`, reruns checks, and accepts or rejects.
6. Codex either patches minor defects directly or issues a narrower follow-up task.

This is a hierarchical orchestrator-specialist pattern with evaluator-optimizer behavior layered on top.

---

## What To Implement

## Phase 1: Make repository instructions production-grade

Priority: highest

### Deliverables

- Add a short root `AGENTS.md` specifically for Codex.
- Keep `AGENTS.md` as an index, not an encyclopedia.
- Split detailed guidance into a structured `docs/` tree.
- Make `CODEX.md` and `CLAUDE.md` point to deeper sources of truth instead of carrying too much detail.

### Recommended docs layout

```text
docs/
  index.md
  architecture/
    index.md
    boundaries.md
    toolchain.md
  workflows/
    hybrid-execution.md
    validation.md
    pr-flow.md
    incident-debugging.md
  plans/
    active/
    completed/
  quality/
    scorecard.md
    test-matrix.md
  references/
    command-reference.md
    env-setup.md
```

### Why this matters

- matches OpenAI's "map + system of record" approach
- reduces context bloat
- gives both agents stable, versioned context

---

## Phase 2: Standardize the Codex -> Claude handoff

Priority: highest

### Deliverables

- Add a reusable Claude execution brief template.
- Add a reusable Codex validation checklist template.
- Add a handoff log format stored in-repo.
- Define task size limits for single Claude runs.

### Files to add

- `docs/workflows/hybrid-execution.md`
- `docs/references/claude-brief-template.md`
- `docs/references/codex-validation-checklist.md`
- `docs/plans/active/README.md`

### Required handoff fields

- goal
- scope
- explicitly allowed files
- explicitly forbidden files
- acceptance criteria
- commands Claude must run
- output format
- rollback/escalation rule

### Policy

- if the task is larger than roughly one engineer-hour or a few hundred lines, split it
- if the task lacks measurable acceptance criteria, do not delegate yet

---

## Phase 3: Convert repeated work into Claude-native commands and skills

Priority: highest

### Deliverables

Add dedicated project workflows for the hybrid model:

- `/hybrid-doc`
- `/hybrid-fix`
- `/hybrid-test`
- `/hybrid-commit`
- `/hybrid-pr`
- `/handoff`

Each should encode:

- when Claude may proceed autonomously
- when Codex must re-check
- expected output sections

### Suggested behavior

- `/hybrid-doc <target>`: Claude runs `/doc`, then emits a summary intended for Codex review.
- `/hybrid-fix <issue>`: Claude applies a bounded fix and runs minimal verification.
- `/hybrid-test`: Claude runs the repository test workflow and reports missing tools explicitly.
- `/hybrid-commit`: only valid after validation artifact exists.
- `/hybrid-pr`: generates a PR description from validated changes only.
- `/handoff <plan-file>`: Claude executes a plan artifact rather than a free-form prompt.

### Why this matters

- lowers prompt variance
- improves repeatability
- aligns with Anthropic's recommendation to use custom slash commands and skills for repeated workflows

---

## Phase 4: Formalize validation as a first-class system

Priority: highest

### Deliverables

- Add a machine-readable validation matrix.
- Add per-language verification bundles.
- Add a "validation artifact" markdown file generated per task.

### Files to add

- `config/validation.yaml`
- `docs/quality/test-matrix.md`
- `docs/workflows/validation.md`
- `artifacts/validations/` directory

### Validation artifact should include

- task id
- plan file
- Claude prompt summary
- changed files
- tests run
- lint/build results
- skipped checks and reasons
- Codex acceptance decision

### Why this matters

- supports the evaluator-optimizer model
- gives traceability across sessions
- makes partial automation safer

---

## Phase 5: Add execution plans as repository artifacts

Priority: high

### Deliverables

- every non-trivial task gets a checked-in plan file
- plans move from `active/` to `completed/`
- plans capture decisions, blockers, and verification results

### Files to add

- `docs/plans/active/TEMPLATE.md`
- `docs/plans/completed/.gitkeep`

### Plan schema

- problem
- context
- constraints
- milestones
- delegated work items
- validation strategy
- open risks
- exit criteria

### Why this matters

- matches OpenAI's execution-plan pattern
- reduces loss of context between sessions
- supports asynchronous hybrid work

---

## Phase 6: Improve repository legibility for agents

Priority: high

### Deliverables

- make build/test/lint commands exhaustive and accurate
- eliminate doc drift between code and scaffolds
- add reference files for tricky subsystems
- encode "gotchas" and invariants in docs, not tribal memory

### Concrete work

- ensure `make build`, `make test`, and `make lint` are reliable
- add missing test scaffolds across all supported languages
- document ownership boundaries and extension patterns in `docs/architecture/`
- add examples and counterexamples to reduce prompt ambiguity

### Why this matters

Agents can only use what is visible and trustworthy in-repo.

---

## Phase 7: Add observability for hybrid-agent operations

Priority: high

### Deliverables

- log Claude invocation metadata
- log validation results
- track failure modes by category
- add a productivity scorecard

### Suggested artifacts

- `artifacts/runs/`
- `artifacts/metrics/weekly-summary.md`
- `docs/quality/scorecard.md`

### Metrics to track

- delegation success rate
- percent of Claude diffs accepted without rework
- median time from prompt to validated result
- test pass rate on first run
- percent of tasks needing Codex direct patching
- percent of tasks blocked by environment/tooling gaps
- token/cost by workflow class if available

### Why this matters

Without observability, you cannot tell whether the hybrid system is improving or just generating more activity.

---

## Phase 8: Introduce safer permission tiers

Priority: medium

### Deliverables

- define permission profiles by task type
- stop using full bypass as the default team workflow
- reserve broad permissions for trusted local execution with post-run validation

### Suggested tiers

- `read-plan`: read-only analysis
- `edit-local`: safe local edits and tests
- `review-only`: diff review and documentation synthesis
- `release-sensitive`: no autonomous push, branch deletion, or infra mutation

### Why this matters

This aligns better with Anthropic's guidance around permission safety and approval fatigue.

---

## Phase 9: Add parallelism carefully

Priority: medium

### Deliverables

- only parallelize independent tasks with disjoint file scopes
- use Codex to assign ownership
- never parallelize work that depends on the same unresolved design decision

### Recommended first uses

- docs generation in parallel with code verification
- independent language-specific changes
- separate review and implementation passes

### Avoid

- parallel edits in overlapping files
- parallel work before architecture is fixed
- parallel Claude tasks without a reconciliation owner

---

## Phase 10: Automate the final mile

Priority: medium

### Deliverables

- let Claude run `/commit` and `/pr` only from validated artifacts
- standardize commit and PR generation on plan + validation context
- make final outputs reproducible

### Required gate

No `/commit` or `/pr` should run unless:

- validation artifact exists
- changed files are in scope
- required checks have passed or been explicitly waived
- Codex marked the task accepted

---

## Recommended Repository Changes

Implement these in order:

1. Add `AGENTS.md` as a short index for Codex-facing guidance.
2. Create the `docs/` system-of-record structure.
3. Add brief/checklist/plan templates.
4. Add `config/validation.yaml`.
5. Add `artifacts/` folders for runs and validations.
6. Convert `.claude/commands/` into hybrid-specific reusable workflows where needed.
7. Add a scorecard and weekly review process.
8. Tighten permission policy after the workflow is measurable.

---

## Success Criteria

You are getting maximum leverage from the hybrid model when:

- Codex rarely has to re-explain repository standards
- Claude tasks arrive pre-scoped and usually stay in scope
- validation is fast and repeatable
- docs and plans reduce context loss between sessions
- the number of successful one-pass delegations trends upward
- environment failures trend downward
- `/commit` and `/pr` become mechanical finalization steps instead of drafting exercises

---

## 30-Day Rollout Plan

### Week 1

- add `AGENTS.md`
- add `docs/` tree
- add plan and handoff templates
- add validation checklist

### Week 2

- create hybrid slash commands/skills
- formalize validation artifacts
- fix repo build/test/lint reliability gaps

### Week 3

- add observability artifacts and weekly metrics
- classify top failure modes
- refine prompts and command templates

### Week 4

- add permission tiers
- gate `/commit` and `/pr` on validation
- review metrics and prune low-value workflow steps

---

## Risks

- Too much instruction volume can reduce agent performance instead of improving it.
- Too much autonomy without validation can create high-confidence bad output.
- Too much validation friction can erase the speed advantage of delegation.
- Parallelism without clear file ownership will create merge and review drag.

The right target is not maximum autonomy.
It is maximum validated throughput.

---

## Sources

OpenAI

- Introducing Codex: https://openai.com/index/introducing-codex/
- Introducing the Codex app: https://openai.com/index/introducing-the-codex-app/
- How OpenAI uses Codex (PDF): https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf
- Harness engineering: leveraging Codex in an agent-first world: https://openai.com/index/harness-engineering/

Anthropic

- How Claude remembers your project: https://code.claude.com/docs/en/memory
- Extend Claude with skills / slash commands: https://code.claude.com/docs/en/slash-commands
- Security: https://code.claude.com/docs/en/security
- Claude Code auto mode: a safer way to skip permissions: https://www.anthropic.com/engineering/claude-code-auto-mode
- Building Effective AI Agents: Architecture Patterns and Implementation Frameworks (PDF): https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf?hsLang=en
- Scaling agentic coding across your organization (PDF): https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf?hsLang=en
- How Anthropic teams use Claude Code (PDF): https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf
