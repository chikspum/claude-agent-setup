"""Tests for Claude bridge timeout classification and recovery behavior."""

from __future__ import annotations

import importlib.util
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
