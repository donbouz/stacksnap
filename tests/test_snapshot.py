"""Tests for the stacksnap.snapshot module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import stacksnap.snapshot as snap


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    """Redirect SNAPSHOT_DIR to a temporary directory for every test."""
    monkeypatch.setattr(snap, "SNAPSHOT_DIR", tmp_path / "snapshots")


# ---------------------------------------------------------------------------
# capture_snapshot
# ---------------------------------------------------------------------------

def test_capture_snapshot_contains_required_keys():
    result = snap.capture_snapshot(name="test-snap")
    for key in ("label", "timestamp", "cwd", "python_version", "git_branch", "pip_packages", "env_vars"):
        assert key in result


def test_capture_snapshot_uses_provided_name():
    result = snap.capture_snapshot(name="my-feature")
    assert result["label"] == "my-feature"


def test_capture_snapshot_generates_label_when_name_omitted():
    result = snap.capture_snapshot()
    assert result["label"].startswith("snap-")


def test_capture_snapshot_handles_missing_tools():
    """_run should return empty string when a tool is not installed."""
    with patch("stacksnap.snapshot._run", return_value=""):
        result = snap.capture_snapshot(name="no-tools")
    assert result["python_version"] == ""
    assert result["node_version"] == ""


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_snapshot_creates_json_file():
    snapshot = snap.capture_snapshot(name="save-test")
    path = snap.save_snapshot(snapshot)
    assert path.exists()
    assert path.suffix == ".json"


def test_load_snapshot_returns_original_data():
    snapshot = snap.capture_snapshot(name="roundtrip")
    snap.save_snapshot(snapshot)
    loaded = snap.load_snapshot("roundtrip")
    assert loaded["label"] == snapshot["label"]
    assert loaded["timestamp"] == snapshot["timestamp"]


def test_load_snapshot_raises_for_missing_label():
    with pytest.raises(FileNotFoundError):
        snap.load_snapshot("does-not-exist")


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

def test_list_snapshots_empty_when_no_dir():
    assert snap.list_snapshots() == []


def test_list_snapshots_returns_all_saved():
    for name in ("alpha", "beta", "gamma"):
        snap.save_snapshot(snap.capture_snapshot(name=name))
    results = snap.list_snapshots()
    labels = {r["label"] for r in results}
    assert labels == {"alpha", "beta", "gamma"}


def test_list_snapshots_sorted_newest_first():
    for name in ("first", "second", "third"):
        snap.save_snapshot(snap.capture_snapshot(name=name))
    results = snap.list_snapshots()
    timestamps = [r["timestamp"] for r in results]
    assert timestamps == sorted(timestamps, reverse=True)


# ---------------------------------------------------------------------------
# delete_snapshot
# ---------------------------------------------------------------------------

def test_delete_snapshot_removes_file():
    snap.save_snapshot(snap.capture_snapshot(name="to-delete"))
    assert snap.delete_snapshot("to-delete") is True
    assert snap.list_snapshots() == []


def test_delete_snapshot_returns_false_for_missing():
    assert snap.delete_snapshot("ghost") is False
