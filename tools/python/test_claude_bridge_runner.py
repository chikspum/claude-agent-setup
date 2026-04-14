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
