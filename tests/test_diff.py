"""Tests for stacksnap.diff module."""

import pytest

from stacksnap.diff import diff_snapshots, format_diff


@pytest.fixture()
def snap_a():
    return {
        "label": "snap-001",
        "timestamp": "2024-01-01T10:00:00",
        "python": "3.11.4",
        "node": "18.17.0",
        "git_branch": "main",
        "git_commit": "abc1234",
        "env_vars": {"DEBUG": "true", "PORT": "8000"},
    }


@pytest.fixture()
def snap_b():
    return {
        "label": "snap-002",
        "timestamp": "2024-01-02T10:00:00",
        "python": "3.12.0",
        "node": "18.17.0",
        "git_branch": "feature/auth",
        "git_commit": "def5678",
        "env_vars": {"DEBUG": "false", "PORT": "8000"},
    }


def test_diff_labels_are_captured(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    assert diff["label_a"] == "snap-001"
    assert diff["label_b"] == "snap-002"


def test_diff_detects_changed_keys(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    assert diff["has_changes"] is True
    assert "python" in diff["changed_keys"]
    assert "git_branch" in diff["changed_keys"]
    assert "git_commit" in diff["changed_keys"]
    assert "env_vars" in diff["changed_keys"]


def test_diff_unchanged_key_not_in_changed_list(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    assert "node" not in diff["changed_keys"]


def test_diff_section_values(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    python_diff = diff["sections"]["python"]
    assert python_diff["status"] == "changed"
    assert python_diff["old"] == "3.11.4"
    assert python_diff["new"] == "3.12.0"


def test_diff_identical_snapshots_has_no_changes(snap_a):
    diff = diff_snapshots(snap_a, snap_a)
    assert diff["has_changes"] is False
    assert diff["changed_keys"] == []


def test_diff_missing_key_in_one_snapshot(snap_a, snap_b):
    del snap_b["node"]
    diff = diff_snapshots(snap_a, snap_b)
    assert "node" in diff["changed_keys"]
    assert diff["sections"]["node"]["old"] == "18.17.0"
    assert diff["sections"]["node"]["new"] is None


def test_diff_key_added_in_second_snapshot(snap_a, snap_b):
    """A key present only in snap_b should appear as added in the diff."""
    snap_b["ruby"] = "3.2.0"
    diff = diff_snapshots(snap_a, snap_b)
    assert "ruby" in diff["changed_keys"]
    assert diff["sections"]["ruby"]["old"] is None
    assert diff["sections"]["ruby"]["new"] == "3.2.0"


def test_format_diff_no_changes(snap_a):
    diff = diff_snapshots(snap_a, snap_a)
    output = format_diff(diff)
    assert "No changes detected" in output


def test_format_diff_shows_changed_keys(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    output = format_diff(diff)
    assert "python" in output
    assert "3.11.4" in output
    assert "3.12.0" in output


def test_format_diff_header_contains_labels(snap_a, snap_b):
    diff = diff_snapshots(snap_a, snap_b)
    output = format_diff(diff)
    assert "snap-001" in output
    assert "snap-002" in output
