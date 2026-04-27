"""Tests for stacksnap.merge."""

import pytest

from stacksnap.merge import (
    _merge_section,
    format_merge_report,
    merge_snapshots,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def snap_a():
    return {
        "label": "snap-a",
        "python": {"version": "3.11.2", "virtualenv": "venv"},
        "node": {"version": "18.0.0"},
        "env_vars": {"DEBUG": "false", "PORT": "8000"},
        "git": {"branch": "main", "commit": "abc123"},
        "tools": {"docker": "24.0.0"},
    }


@pytest.fixture()
def snap_b():
    return {
        "label": "snap-b",
        "python": {"version": "3.12.0", "virtualenv": "venv"},
        "node": {"version": "20.0.0"},
        "env_vars": {"DEBUG": "true", "API_KEY": "secret"},
        "git": {"branch": "feature/x", "commit": "def456"},
        "tools": {"docker": "24.0.0"},
    }


# ---------------------------------------------------------------------------
# _merge_section
# ---------------------------------------------------------------------------

def test_merge_section_override_wins():
    base = {"a": "1", "b": "2"}
    over = {"a": "99", "c": "3"}
    merged, conflicts = _merge_section(base, over, strategy="override")
    assert merged["a"] == "99"
    assert merged["b"] == "2"
    assert merged["c"] == "3"
    assert "a" in conflicts


def test_merge_section_keep_preserves_base():
    base = {"a": "1"}
    over = {"a": "99"}
    merged, conflicts = _merge_section(base, over, strategy="keep")
    assert merged["a"] == "1"
    assert "a" in conflicts


def test_merge_section_no_conflict_when_equal():
    base = {"a": "1"}
    over = {"a": "1"}
    _, conflicts = _merge_section(base, over)
    assert conflicts == []


def test_merge_section_new_keys_added():
    base = {"a": "1"}
    over = {"b": "2"}
    merged, conflicts = _merge_section(base, over)
    assert "b" in merged
    assert conflicts == []


# ---------------------------------------------------------------------------
# merge_snapshots
# ---------------------------------------------------------------------------

def test_merge_snapshots_label_set(snap_a, snap_b):
    merged, _ = merge_snapshots(snap_a, snap_b, name="my-merge")
    assert merged["label"] == "my-merge"


def test_merge_snapshots_override_strategy(snap_a, snap_b):
    merged, conflicts = merge_snapshots(snap_a, snap_b, strategy="override")
    assert merged["python"]["version"] == "3.12.0"
    assert "python" in conflicts


def test_merge_snapshots_keep_strategy(snap_a, snap_b):
    merged, conflicts = merge_snapshots(snap_a, snap_b, strategy="keep")
    assert merged["python"]["version"] == "3.11.2"
    assert "python" in conflicts


def test_merge_snapshots_no_conflict_section(snap_a, snap_b):
    # tools are identical in both fixtures
    _, conflicts = merge_snapshots(snap_a, snap_b)
    assert "tools" not in conflicts


def test_merge_snapshots_new_env_key_added(snap_a, snap_b):
    merged, _ = merge_snapshots(snap_a, snap_b)
    assert merged["env_vars"].get("API_KEY") == "secret"


def test_merge_snapshots_invalid_strategy(snap_a, snap_b):
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_snapshots(snap_a, snap_b, strategy="bad")


# ---------------------------------------------------------------------------
# format_merge_report
# ---------------------------------------------------------------------------

def test_format_merge_report_no_conflicts():
    report = format_merge_report({}, "override")
    assert "no conflicts" in report.lower()


def test_format_merge_report_lists_sections():
    conflicts = {"python": ["version"], "env_vars": ["DEBUG"]}
    report = format_merge_report(conflicts, "keep")
    assert "python" in report
    assert "env_vars" in report
    assert "keep" in report
