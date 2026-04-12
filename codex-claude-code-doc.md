# Codex Claude Code Doc

```yaml
schema_version: codex_claude_project_doc/v1
project:
  name: claude-agent-setup
  repository_path: /home/ubuntu/claude-agent-setup
  operating_mode: codex_orchestrates_claude
  production_default_flow: codex -> plan -> claude_code_execution -> codex_validation

agents:
  codex:
    role: controller_and_validator
    responsibilities:
      - task_intake
      - repository_inspection
      - task_decomposition
      - plan_management
      - claude_brief_construction
      - diff_review
      - local_validation
      - acceptance_decision
      - user_facing_status
    default_execution_mode: direct_only_for_trivial_or_lower_risk_work
    source_of_truth:
      - CODEX.md
      - docs/workflows/hybrid-execution.md
      - docs/workflows/validation.md
  claude_code:
    role: scoped_executor
    responsibilities:
      - bounded_repo_edits
      - claude_command_execution
      - repo_local_command_execution
      - changed_file_reporting
      - check_reporting
      - blocker_reporting
    completion_rule: not_final_until_validated_by_codex
    source_of_truth:
      - CLAUDE.md
      - .claude/commands/
      - docs/workflows/hybrid-execution.md

workflow:
  steps:
    - id: inspect
      actor: codex
      action: read_target_files_and_current_repo_state
    - id: plan
      actor: codex
      action: define_scope_constraints_and_acceptance
      artifacts:
        - docs/plans/active/
    - id: brief
      actor: codex
      action: create_constrained_claude_execution_brief
    - id: execute
      actor: claude_code
      action: perform_bounded_work
    - id: log
      actor: claude_code_or_codex
      action: record_material_execution_details
      artifacts:
        - artifacts/runs/
    - id: validate
      actor: codex
      action: rerun_checks_review_diff_and_verify_scope
      artifacts:
        - artifacts/validations/
    - id: decide
      actor: codex
      action: accept_patch_or_rescope

handoff_contract:
  required_fields:
    - repo_path
    - goal
    - required_changes
    - forbidden_changes
    - constraints
    - verification_commands
    - expected_final_response_format
  template: docs/references/claude-brief-template.md
  command_entrypoint: .claude/commands/handoff.md

command_surface:
  repo_local:
    build: bash scripts/build.sh
    test: bash scripts/test.sh
    lint: bash scripts/lint.sh
    handoff_bridge:
      - bash scripts/run_claude_handoff.sh docs/plans/active/<plan-file>.md
      - make handoff PLAN=docs/plans/active/<plan-file>.md
    delegate_runner:
      - python3 scripts/delegate_to_claude.py --goal "..." --change "path: exact change"
      - make delegate GOAL="..."
    strict_verify:
      - make doctor
      - make policy-check
      - make metrics-check
      - make verify
  claude_commands:
    primary:
      - /build
      - /doc
      - /review
      - /test
      - /status
      - /commit
      - /pr
      - /init
      - /handoff <plan-file>
      - /hybrid-doc <target>
      - /hybrid-test
      - /hybrid-fix <issue>
      - /hybrid-commit
      - /hybrid-pr
    ownership_rule: claude_commands_are_runtime_features_of_claude_not_native_codex_commands

validation:
  minimum_checks:
    - git status --short
    - git diff --stat
    - git diff
    - task_specific_tests
    - task_specific_build_or_lint_checks
    - scope_match_review
  machine_policy: config/validation.yaml
  policy_automation:
    - python3 scripts/check_artifacts.py
    - python3 scripts/check_docs_drift.py
    - python3 scripts/generate_metrics_summary.py --check
  acceptance_requirements:
    - changed_files_are_in_scope
    - required_checks_ran_or_were_explicitly_skipped
    - missing_tools_are_reported
    - degraded_paths_are_reported
    - docs_do_not_overclaim_behavior
    - codex_records_acceptance_decision

artifacts:
  plans:
    active: docs/plans/active/
    completed: docs/plans/completed/
    purpose: define_scope_and_execution_plan_for_non_trivial_work
  runs:
    directory: artifacts/runs/
    purpose: record_execution_details_and_environment_behavior
  validations:
    directory: artifacts/validations/
    purpose: record_codex_review_checks_and_acceptance
  metrics:
    summary: artifacts/metrics/summary.json
    generator: python3 scripts/generate_metrics_summary.py
    purpose: compact_machine_readable_operational_snapshot

runtime_profiles:
  codex:
    recommended_profiles:
      safe:
        sandbox: workspace-write
        approval_mode: on-request
      full-access:
        sandbox: danger-full-access
        approval_mode: on-request
    reference: docs/references/codex-runtime-profiles.md

restrictions:
  baseline_forbidden_paths:
    - secrets/
    - .ssh/
    - .env
    - "*.pem"
    - "*.key"
  baseline_forbidden_commands:
    - git reset --hard
    - ssh
  enforcement_layers:
    - repo_policy
    - claude_runtime_settings
    - outer_launcher_or_sandbox
  claude_runtime_settings: .claude/settings.json
  reference: docs/references/restrictions.md

strict_toolchain:
  required_tools:
    python3: ">=3.11"
    uv: ">=0.4"
    go: ">=1.22"
    gplusplus: present
    cmake: ">=3.22"
    ctest: ">=3.22"
    clang_format: ">=14"
  doctor_command: make doctor
  full_gate_command: make verify
  degraded_mode_rule: allowed_for_local_agent_work_but_not_for_production_acceptance

ci:
  workflow_file: .github/workflows/verify.yml
  main_job: make verify
  purpose: enforce_strict_verification_in_controlled_environment

release_gate:
  reference: docs/references/production-gate.md
  required_flags_from_metrics_summary:
    - docs_and_command_surface_aligned
    - runtime_profile_guidance_present
    - restriction_policy_present
    - delegated_docs_task_verified
    - delegated_code_task_verified
    - machine_readable_summary_present
    - production_prep_completed

examples:
  delegated_docs_only_task:
    run_log: artifacts/runs/2026-04-09-claude-handoff-smoke-run-01.md
    completed_plan: docs/plans/completed/2026-04-09-claude-handoff-smoke.md
    validation: artifacts/validations/2026-04-09-claude-handoff-smoke.md
  delegated_code_edit_task:
    run_log: artifacts/runs/2026-04-09-python-reverse-skill-run-01.md
    completed_plan: docs/plans/completed/2026-04-09-python-reverse-skill.md
    validation: artifacts/validations/2026-04-09-python-reverse-skill.md
```
