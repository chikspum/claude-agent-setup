"""Tests for Claude bridge timeout classification and recovery behavior."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bridge = load_module(
    "run_claude_from_plan_under_test",
    REPO_ROOT / "scripts" / "run_claude_from_plan.py",
)
delegate = load_module(
    "delegate_to_claude_under_test",
    REPO_ROOT / "scripts" / "delegate_to_claude.py",
)


def configure_temp_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(bridge, "ROOT", tmp_path)
    monkeypatch.setattr(
        bridge, "DEBUG_ARTIFACT_DIR", tmp_path / "artifacts" / "debug" / "claude-bridge"
    )


def test_timeout_without_meaningful_diff_is_failure(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="no-diff",
        required_changes=["allowed.py: optional file"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="timeout",
        timeout_seconds=5,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "failure"
    assert inspection.meaningful_diff is False
    assert inspection.changed_files == []
    assert inspection.debug_artifact_path is not None
    assert Path(inspection.debug_artifact_path).exists()


def test_timeout_with_in_scope_diff_and_passing_checks_is_partial_success(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "allowed.py").write_text("print('ok')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="pass-partial",
        required_changes=["allowed.py: add implementation"],
        validation_commands=["python3 -c 'print(1)'"],
        before_snapshot=before_snapshot,
        stdout="partial stdout",
        stderr="",
        timeout_seconds=5,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "partial_success"
    assert inspection.out_of_scope_files == []
    assert inspection.follow_up_recommended is False
    assert inspection.validation_checks[0].result == "PASS"
    assert inspection.materialization_state == "validated_success"


def test_timeout_with_in_scope_diff_and_failing_checks_is_salvageable_partial_success(
    monkeypatch, tmp_path
):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "module.py").write_text("print('still broken')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="salvageable",
        required_changes=["module.py: add implementation"],
        validation_commands=["python3 -c 'import sys; sys.exit(1)'"],
        before_snapshot=before_snapshot,
        stdout="partial stdout",
        stderr="timeout",
        timeout_seconds=5,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "partial_success"
    assert inspection.repo_broken is True
    assert inspection.follow_up_recommended is True
    assert inspection.follow_up_actions
    assert inspection.validation_checks[0].result == "FAIL"
    assert inspection.materialization_state == "validated_partial"


def test_timeout_with_out_of_scope_diff_is_failure(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "unexpected.py").write_text("print('oops')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="out-of-scope",
        required_changes=["allowed.py: only file in scope"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="partial stdout",
        stderr="timeout",
        timeout_seconds=5,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "failure"
    assert inspection.out_of_scope_files == ["unexpected.py"]


def test_directory_scope_treats_descendants_as_in_scope(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()
    (package_dir / "module.py").write_text("print('ok')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="directory-scope",
        required_changes=["pkg: create the package and files within it"],
        validation_commands=["python3 -c 'print(1)'"],
        before_snapshot=before_snapshot,
        stdout="partial stdout",
        stderr="timeout",
        timeout_seconds=5,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "partial_success"
    assert "pkg/module.py" in inspection.in_scope_files
    assert inspection.out_of_scope_files == []


def test_allowed_prefix_scope_supports_glob_style_package_paths():
    policy = bridge.build_scope_policy(
        [
            "tools/python/pagination/**: allow package work",
            "tools/python/test_pagination_engine.py: allow tests",
        ]
    )

    assert "tools/python/pagination" in policy.allowed_path_prefixes
    assert "tools/python/pagination" in policy.allowed_new_paths
    assert bridge.is_path_in_scope("tools/python/pagination/models.py", policy) is True
    assert bridge.is_path_in_scope("tools/python/other.py", policy) is False


def test_path_created_only_is_classified_as_recoverable_partial_success(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "pkg").mkdir()

    inspection = bridge.inspect_abnormal_run(
        task_id="path-created-only",
        required_changes=["pkg/**: create a new package under pkg"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="partial stdout",
        stderr="timeout",
        timeout_seconds=20,
        process_exit_code=None,
        timed_out=True,
        early_abort_triggered=True,
        guidance=bridge.OrchestrationGuidance(
            mode="sliced_edit",
            reason="oversized task",
            selected_work_items=["create package skeleton only"],
            slice_plan=["implement models + fingerprinting only"],
            recommended_next_slice="implement models + fingerprinting only",
        ),
    )

    assert inspection.outcome == "partial_success"
    assert inspection.materialization_state == "path_created_only"
    assert inspection.early_abort_triggered is True
    assert inspection.follow_up_recommended is True
    assert inspection.allowed_path_prefixes == ["pkg"]
    assert inspection.recommended_next_slice == "implement models + fingerprinting only"

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["materialization_state"] == "path_created_only"
    assert payload["early_abort_triggered"] is True
    assert payload["allowed_path_prefixes"] == ["pkg"]


def test_early_abort_triggers_for_path_created_only_in_edit_mode():
    assert (
        bridge.should_early_abort(
            permission_mode="acceptEdits",
            elapsed_seconds=10,
            timeout_seconds=20,
            materialization_state="path_created_only",
            out_of_scope_files=[],
        )
        is True
    )
    assert (
        bridge.should_early_abort(
            permission_mode="acceptEdits",
            elapsed_seconds=5,
            timeout_seconds=20,
            materialization_state="path_created_only",
            out_of_scope_files=[],
        )
        is False
    )
    assert (
        bridge.should_early_abort(
            permission_mode="dontAsk",
            elapsed_seconds=10,
            timeout_seconds=20,
            materialization_state="path_created_only",
            out_of_scope_files=[],
        )
        is False
    )


def test_oversized_edit_task_uses_sliced_execution_guidance(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: pagination-phase-1",
                "",
                "## Problem",
                "",
                "Build the pagination engine.",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - tools/python/pagination/**: create runtime package",
                "  - tools/python/test_pagination_engine.py: add tests",
                "  - docs/references/pagination-engine.md: add docs",
                "  - tools/python/pyproject.toml: add packaging hooks",
                "- files that must not change:",
                "  - unrelated files",
                "- public interfaces that must remain stable:",
                "  - existing bridge CLI args",
                "",
                "## Claude Work Items",
                "",
                "- implement models + fingerprinting + detector",
                "- implement runtime + navigator + browser helpers",
                "- add tests + pyproject integration",
                "- polish docs + limitations",
                "",
                "## Validation Strategy",
                "",
                "- run focused tests",
            ]
        ),
        encoding="utf-8",
    )

    task_id, brief, guidance = bridge.build_brief(plan, "acceptEdits")

    assert task_id == "pagination-phase-1"
    assert guidance.mode == "sliced_edit"
    assert guidance.selected_work_items == [
        "implement core models + fingerprinting + detector only"
    ]
    assert "Execution mode: sliced_edit" in brief
    assert "Current execution slice:" in brief
    assert "implement core models + fingerprinting + detector only" in brief


def test_read_only_probe_mode_uses_compact_brief(tmp_path):
    plan = tmp_path / "probe.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: probe-pagination",
                "",
                "## Problem",
                "",
                "Design the pagination package layout.",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - tools/python/pagination/**: future package work",
                "- files that must not change:",
                "  - unrelated files",
                "- public interfaces that must remain stable:",
                "  - existing bridge CLI args",
                "",
                "## Claude Work Items",
                "",
                "- propose architecture",
                "- propose files",
                "- propose first slice",
                "",
                "## Validation Strategy",
                "",
                "- keep the output compact",
            ]
        ),
        encoding="utf-8",
    )

    _, brief, guidance = bridge.build_brief(plan, "dontAsk")

    assert guidance.mode == "micro_probe"
    assert "Mode: micro-probe" in brief
    assert "## Architecture" in brief
    assert "## Files" in brief
    assert "## Slice 1" in brief
    assert "read-only analysis only" in brief


def test_delegate_runner_recognizes_partial_success_outcome():
    stdout = "\n".join(
        [
            "## Bridge Inspection",
            "- outcome: partial_success",
            "- debug_artifact: /tmp/debug.json",
        ]
    )

    assert delegate.classify_bridge_outcome(75, stdout) == "partial_success"
    assert delegate.extract_bridge_field(stdout, "debug_artifact") == "/tmp/debug.json"


# ---------------------------------------------------------------------------
# Structured validation command parsing
# ---------------------------------------------------------------------------


def test_parse_validation_commands_extracts_cmd_prefixed_lines():
    lines = [
        "- cmd: python3 -m py_compile scripts/run_claude_from_plan.py",
        "- cmd: python3 -m pytest -q tools/python/test_claude_bridge_runner.py",
        "- report skipped checks and why",
        "- state whether files stayed in scope",
        "  some indented prose",
    ]
    commands = bridge.parse_validation_commands(lines)
    assert commands == [
        "python3 -m py_compile scripts/run_claude_from_plan.py",
        "python3 -m pytest -q tools/python/test_claude_bridge_runner.py",
    ]


def test_parse_validation_commands_empty_when_no_cmd_prefix():
    lines = [
        "- run the smallest relevant repo-local checks for the touched area",
        "- report skipped checks and why",
        "- state whether files stayed in scope",
    ]
    commands = bridge.parse_validation_commands(lines)
    assert commands == []


def test_parse_validation_commands_ignores_blank_cmd_values():
    lines = [
        "- cmd:",
        "- cmd:   ",
        "- cmd: python3 -m pytest -q tools/python/test_claude_bridge_runner.py",
    ]
    commands = bridge.parse_validation_commands(lines)
    assert commands == [
        "python3 -m pytest -q tools/python/test_claude_bridge_runner.py",
    ]


def test_extract_plan_scope_uses_cmd_prefix_for_validation(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: cmd-parse-test",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - scripts/foo.py: update implementation",
                "- files that must not change:",
                "  - unrelated files",
                "",
                "## Validation Strategy",
                "",
                "- cmd: python3 -m py_compile scripts/foo.py",
                "- cmd: python3 -m pytest -q tools/python/test_foo.py",
                "- report skipped checks and why",
            ]
        ),
        encoding="utf-8",
    )

    task_id, required_changes, forbidden_changes, validation_commands = bridge.extract_plan_scope(
        plan
    )

    assert task_id == "cmd-parse-test"
    assert required_changes == ["scripts/foo.py: update implementation"]
    assert validation_commands == [
        "python3 -m py_compile scripts/foo.py",
        "python3 -m pytest -q tools/python/test_foo.py",
    ]
    assert "report skipped checks and why" not in validation_commands


def test_delegate_render_plan_prefixes_verify_items_with_cmd():
    plan_text = delegate.render_plan(
        task_id="cmd-prefix-test",
        owner="Codex",
        status="active",
        goal="Fix the bridge.",
        required_changes=["scripts/run_claude_from_plan.py: harden parsing"],
        forbidden_changes=["unrelated files"],
        constraints=["existing CLI entrypoints"],
        verification=[
            "python3 -m py_compile scripts/run_claude_from_plan.py",
            "python3 -m pytest -q tools/python/test_claude_bridge_runner.py",
        ],
        claude_work_items=[],
    )

    assert "- cmd: python3 -m py_compile scripts/run_claude_from_plan.py" in plan_text
    assert "- cmd: python3 -m pytest -q tools/python/test_claude_bridge_runner.py" in plan_text


def test_delegate_render_plan_no_verify_uses_prose_fallback():
    plan_text = delegate.render_plan(
        task_id="prose-fallback-test",
        owner="Codex",
        status="active",
        goal="Fix the bridge.",
        required_changes=[],
        forbidden_changes=[],
        constraints=[],
        verification=[],
        claude_work_items=[],
    )

    assert "run the smallest relevant repo-local checks for the touched area" in plan_text
    assert "- cmd:" not in plan_text


# ---------------------------------------------------------------------------
# Execution failure (non-zero exit, not timeout)
# ---------------------------------------------------------------------------


def test_execution_failure_non_zero_exit_without_diff_is_failure(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="nonzero-no-diff",
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="error: claude exited unexpectedly",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    assert inspection.outcome == "failure"
    assert inspection.meaningful_diff is False
    assert inspection.changed_files == []
    assert inspection.debug_artifact_path is not None
    assert Path(inspection.debug_artifact_path).exists()


def test_execution_failure_non_zero_exit_with_in_scope_diff_is_partial_success(
    monkeypatch, tmp_path
):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("print('partial')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="nonzero-with-diff",
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=["python3 -c 'print(1)'"],
        before_snapshot=before_snapshot,
        stdout="partial stdout before crash",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    assert inspection.outcome == "partial_success"
    assert "scripts/foo.py" in inspection.in_scope_files
    assert inspection.validation_checks[0].result == "PASS"


# ---------------------------------------------------------------------------
# materialized_but_unvalidated state (files created, no validation commands provided)
# ---------------------------------------------------------------------------


def test_materialized_but_unvalidated_without_validation_commands(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    (tmp_path / "module.py").write_text("print('done')\n", encoding="utf-8")

    inspection = bridge.inspect_abnormal_run(
        task_id="materialized-but-unvalidated",
        required_changes=["module.py: implement module"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="some output",
        stderr="",
        timeout_seconds=60,
        process_exit_code=None,
        timed_out=True,
    )

    assert inspection.outcome == "partial_success"
    assert inspection.materialization_state == "materialized_but_unvalidated"
    assert inspection.validation_checks == []
    assert "module.py" in inspection.in_scope_files


# ---------------------------------------------------------------------------
# Package bootstrap slicing
# ---------------------------------------------------------------------------


def test_package_bootstrap_slice_recommended_for_new_package_task(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: new-package-bootstrap",
                "",
                "## Problem",
                "",
                "Create a new Python package from scratch.",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - tools/python/newpkg/**: create the package",
                "  - tools/python/newpkg/__init__.py: exports",
                "  - tools/python/test_newpkg.py: add tests",
                "  - tools/python/pyproject.toml: register package",
                "- files that must not change:",
                "  - unrelated files",
                "",
                "## Claude Work Items",
                "",
                "- create package structure",
                "- implement core logic",
                "- add tests",
                "",
                "## Validation Strategy",
                "",
                "- run tests",
            ]
        ),
        encoding="utf-8",
    )

    task_id, brief, guidance = bridge.build_brief(plan, "acceptEdits")

    assert task_id == "new-package-bootstrap"
    assert guidance.mode == "sliced_edit"
    assert "create package skeleton" in guidance.selected_work_items[0]
    assert "create package skeleton" in guidance.slice_plan[0]


# ---------------------------------------------------------------------------
# Retry gating
# ---------------------------------------------------------------------------


def test_retry_eligible_for_execution_failure_no_progress_only():
    assert bridge.is_retry_eligible("execution_failure", "no_progress") is True
    assert bridge.is_retry_eligible("timeout", "no_progress") is False
    assert bridge.is_retry_eligible("execution_failure", "materialized_but_unvalidated") is False
    assert bridge.is_retry_eligible("execution_failure", "path_created_only") is False
    assert bridge.is_retry_eligible("clean_exit", "no_progress") is False
    assert bridge.is_retry_eligible("early_abort", "no_progress") is False


# ---------------------------------------------------------------------------
# Debug artifact payload contains run and acceptance outcomes
# ---------------------------------------------------------------------------


def test_debug_artifact_contains_run_and_acceptance_outcomes(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="run-acceptance-split",
        required_changes=["scripts/foo.py: fix"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    assert inspection.run_outcome == "execution_failure"
    assert inspection.acceptance_outcome == "failure"
    assert inspection.retry_eligible is True

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["run_outcome"] == "execution_failure"
    assert payload["acceptance_outcome"] == "failure"
    assert payload["retry_eligible"] is True
    assert "failure_kind" in payload


# ---------------------------------------------------------------------------
# docs-vs-code overclaim check
# ---------------------------------------------------------------------------


def test_check_docs_overclaim_flags_docs_only_changes():
    warnings = bridge.check_docs_overclaim(["docs/design.md", "docs/api.md"])
    assert len(warnings) == 1
    assert "docs changed without runtime support" in warnings[0]
    assert "docs/design.md" in warnings[0]


def test_check_docs_overclaim_does_not_flag_mixed_docs_and_runtime():
    warnings = bridge.check_docs_overclaim(["docs/design.md", "scripts/run_claude_from_plan.py"])
    assert warnings == []


def test_check_docs_overclaim_does_not_flag_empty_change_set():
    assert bridge.check_docs_overclaim([]) == []


def test_check_docs_overclaim_does_not_flag_runtime_only_changes():
    assert bridge.check_docs_overclaim(["scripts/run_claude_from_plan.py"]) == []


def test_check_docs_overclaim_does_not_flag_docs_plus_tests_but_no_runtime():
    # Tests without runtime is not a docs overclaim; runtime layer is what matters.
    warnings = bridge.check_docs_overclaim(["docs/design.md", "tools/python/test_foo.py"])
    # docs + tests only — runtime absent → flagged
    assert len(warnings) == 1


# ---------------------------------------------------------------------------
# Debug artifact carries plan_path
# ---------------------------------------------------------------------------


def test_debug_artifact_contains_plan_path(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)
    fake_plan = "/some/repo/docs/plans/active/my-plan.md"

    inspection = bridge.inspect_abnormal_run(
        task_id="plan-path-test",
        plan_path=fake_plan,
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["plan_path"] == fake_plan


def test_debug_artifact_plan_path_is_none_when_not_provided(monkeypatch, tmp_path):
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="plan-path-absent",
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["plan_path"] is None


# ---------------------------------------------------------------------------
# Retry execution path
# ---------------------------------------------------------------------------


def test_run_claude_retries_once_on_execution_failure_with_no_progress(monkeypatch, tmp_path):
    """run_claude should call the subprocess exactly twice when the first attempt
    produces execution_failure with no_progress and _allow_retry is True."""
    import io
    import subprocess as _subprocess

    configure_temp_root(monkeypatch, tmp_path)
    monkeypatch.setattr(bridge, "git_diff_stats", lambda paths: "none")

    plan = tmp_path / "plan.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: retry-exec-test",
                "",
                "## Problem",
                "",
                "Test retry once on execution failure.",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - scripts/foo.py: fix bug",
                "- files that must not change:",
                "  - unrelated files",
                "",
                "## Claude Work Items",
                "",
                "- fix the bug",
                "",
                "## Validation Strategy",
                "",
                "- run tests",
            ]
        ),
        encoding="utf-8",
    )

    popen_calls: list = []

    class FakeProcess:
        def __init__(self):
            self.stdin = io.StringIO()

        def poll(self):
            return 1  # non-zero exit immediately → execution_failure

        def wait(self, timeout=None):
            pass

        def terminate(self):
            pass

        def kill(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_popen(cmd, **kwargs):
        popen_calls.append(list(cmd))
        return FakeProcess()

    monkeypatch.setattr(_subprocess, "Popen", fake_popen)

    bridge.run_claude(plan, "acceptEdits", "fake-claude", 30, "text", True)

    # First attempt: execution_failure + no_progress → retry once
    # Second attempt: same outcome but _allow_retry=False → no third call
    assert len(popen_calls) == 2


def test_run_claude_does_not_retry_when_allow_retry_false(monkeypatch, tmp_path):
    """With _allow_retry=False, run_claude must not retry even if eligible."""
    import io
    import subprocess as _subprocess

    configure_temp_root(monkeypatch, tmp_path)
    monkeypatch.setattr(bridge, "git_diff_stats", lambda paths: "none")

    plan = tmp_path / "plan.md"
    plan.write_text(
        "\n".join(
            [
                "# Plan",
                "",
                "## Metadata",
                "",
                "- task_id: no-retry-test",
                "",
                "## Problem",
                "",
                "Test no retry.",
                "",
                "## Scope",
                "",
                "- files expected to change:",
                "  - scripts/foo.py: fix bug",
                "- files that must not change:",
                "  - unrelated files",
                "",
                "## Claude Work Items",
                "",
                "- fix the bug",
                "",
                "## Validation Strategy",
                "",
                "- run tests",
            ]
        ),
        encoding="utf-8",
    )

    popen_calls: list = []

    class FakeProcess:
        def __init__(self):
            self.stdin = io.StringIO()

        def poll(self):
            return 1

        def wait(self, timeout=None):
            pass

        def terminate(self):
            pass

        def kill(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_popen(cmd, **kwargs):
        popen_calls.append(list(cmd))
        return FakeProcess()

    monkeypatch.setattr(_subprocess, "Popen", fake_popen)

    bridge.run_claude(plan, "acceptEdits", "fake-claude", 30, "text", True, _allow_retry=False)

    assert len(popen_calls) == 1


# ---------------------------------------------------------------------------
# Runtime-health fields in debug artifacts
# ---------------------------------------------------------------------------


def test_debug_artifact_contains_runtime_health_fields(monkeypatch, tmp_path):
    """elapsed_seconds and is_retry_attempt must appear in abnormal-run artifacts."""
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="runtime-health-test",
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
        elapsed_seconds=42.5,
        is_retry_attempt=True,
    )

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["elapsed_seconds"] == 42.5
    assert payload["is_retry_attempt"] is True


def test_debug_artifact_runtime_health_defaults_to_initial_run(monkeypatch, tmp_path):
    """When elapsed_seconds and is_retry_attempt are omitted they default safely."""
    configure_temp_root(monkeypatch, tmp_path)
    before_snapshot = bridge.capture_repo_snapshot(tmp_path)

    inspection = bridge.inspect_abnormal_run(
        task_id="runtime-health-defaults",
        required_changes=["scripts/foo.py: fix bug"],
        validation_commands=[],
        before_snapshot=before_snapshot,
        stdout="",
        stderr="exit status 1",
        timeout_seconds=120,
        process_exit_code=1,
        timed_out=False,
    )

    payload = json.loads(Path(inspection.debug_artifact_path).read_text(encoding="utf-8"))
    assert payload["elapsed_seconds"] == 0.0
    assert payload["is_retry_attempt"] is False
