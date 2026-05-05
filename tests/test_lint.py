"""Tests for stacksnap.lint."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.lint import (
    WARN_LABEL_GENERIC,
    WARN_MISSING_ENV_VARS,
    WARN_MISSING_NODE,
    WARN_MISSING_PYTHON,
    WARN_NO_PACKAGES,
    INFO_LARGE_ENV,
    format_lint_report,
    lint_snapshot,
    lint_snapshot_file,
)


@pytest.fixture()
def clean_snapshot() -> dict:
    return {
        "label": "my-feature-branch",
        "python": {"version": "3.11.4", "packages": {"requests": "2.31.0"}},
        "node": {"version": "20.5.0"},
        "env_vars": {"DATABASE_URL": "postgres://localhost/dev"},
    }


def test_clean_snapshot_returns_no_issues(clean_snapshot):
    assert lint_snapshot(clean_snapshot) == []


def test_generic_label_triggers_warning(clean_snapshot):
    clean_snapshot["label"] = "snapshot-1234567890"
    issues = lint_snapshot(clean_snapshot)
    assert WARN_LABEL_GENERIC in issues


def test_empty_label_triggers_warning(clean_snapshot):
    clean_snapshot["label"] = ""
    issues = lint_snapshot(clean_snapshot)
    assert WARN_LABEL_GENERIC in issues


def test_missing_python_section_triggers_warning(clean_snapshot):
    del clean_snapshot["python"]
    issues = lint_snapshot(clean_snapshot)
    assert WARN_MISSING_PYTHON in issues


def test_python_without_version_triggers_warning(clean_snapshot):
    clean_snapshot["python"] = {"packages": {}}
    issues = lint_snapshot(clean_snapshot)
    assert WARN_MISSING_PYTHON in issues


def test_python_without_packages_triggers_warning(clean_snapshot):
    clean_snapshot["python"] = {"version": "3.11.4"}
    issues = lint_snapshot(clean_snapshot)
    assert WARN_NO_PACKAGES in issues


def test_missing_node_section_triggers_warning(clean_snapshot):
    del clean_snapshot["node"]
    issues = lint_snapshot(clean_snapshot)
    assert WARN_MISSING_NODE in issues


def test_empty_env_vars_triggers_warning(clean_snapshot):
    clean_snapshot["env_vars"] = {}
    issues = lint_snapshot(clean_snapshot)
    assert WARN_MISSING_ENV_VARS in issues


def test_large_env_vars_triggers_info(clean_snapshot):
    clean_snapshot["env_vars"] = {f"KEY_{i}": str(i) for i in range(51)}
    issues = lint_snapshot(clean_snapshot)
    assert INFO_LARGE_ENV in issues


def test_lint_snapshot_file_reads_json(tmp_path, clean_snapshot):
    snap_file = tmp_path / "snap.json"
    snap_file.write_text(json.dumps(clean_snapshot))
    assert lint_snapshot_file(snap_file) == []


def test_lint_snapshot_file_handles_bad_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    issues = lint_snapshot_file(bad)
    assert len(issues) == 1
    assert "cannot read" in issues[0]


def test_format_lint_report_clean():
    report = format_lint_report("snap-abc", [])
    assert report == "snap-abc: OK"


def test_format_lint_report_with_issues():
    issues = [WARN_MISSING_PYTHON, WARN_MISSING_ENV_VARS]
    report = format_lint_report("snap-xyz", issues)
    assert "snap-xyz: 2 issue(s)" in report
    assert WARN_MISSING_PYTHON in report
    assert WARN_MISSING_ENV_VARS in report
