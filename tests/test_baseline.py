"""Tests for stacksnap/baseline.py"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap import baseline as bl


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write_snap(snap_dir: Path, snap_id: str, data: dict) -> None:
    (snap_dir / f"{snap_id}.json").write_text(json.dumps(data), encoding="utf-8")


# --- set / get / clear ---

def test_set_baseline_returns_true_when_new(snap_dir):
    assert bl.set_baseline("snap-001", snap_dir) is True


def test_set_baseline_returns_false_when_same(snap_dir):
    bl.set_baseline("snap-001", snap_dir)
    assert bl.set_baseline("snap-001", snap_dir) is False


def test_get_baseline_returns_none_when_unset(snap_dir):
    assert bl.get_baseline(snap_dir) is None


def test_get_baseline_returns_set_id(snap_dir):
    bl.set_baseline("snap-abc", snap_dir)
    assert bl.get_baseline(snap_dir) == "snap-abc"


def test_set_baseline_overwrites_previous(snap_dir):
    bl.set_baseline("snap-001", snap_dir)
    bl.set_baseline("snap-002", snap_dir)
    assert bl.get_baseline(snap_dir) == "snap-002"


def test_clear_baseline_returns_true_when_exists(snap_dir):
    bl.set_baseline("snap-001", snap_dir)
    assert bl.clear_baseline(snap_dir) is True


def test_clear_baseline_returns_false_when_missing(snap_dir):
    assert bl.clear_baseline(snap_dir) is False


def test_clear_baseline_removes_entry(snap_dir):
    bl.set_baseline("snap-001", snap_dir)
    bl.clear_baseline(snap_dir)
    assert bl.get_baseline(snap_dir) is None


# --- diff_against_baseline ---

def test_diff_raises_when_no_baseline(snap_dir):
    _write_snap(snap_dir, "snap-002", {"python": "3.11"})
    with pytest.raises(ValueError, match="No baseline"):
        bl.diff_against_baseline("snap-002", snap_dir)


def test_diff_raises_when_snapshot_missing(snap_dir):
    _write_snap(snap_dir, "snap-001", {"python": "3.10"})
    bl.set_baseline("snap-001", snap_dir)
    with pytest.raises(FileNotFoundError):
        bl.diff_against_baseline("snap-999", snap_dir)


def test_diff_empty_when_identical(snap_dir):
    data = {"python": "3.11", "node": "20"}
    _write_snap(snap_dir, "snap-001", data)
    _write_snap(snap_dir, "snap-002", data)
    bl.set_baseline("snap-001", snap_dir)
    diff = bl.diff_against_baseline("snap-002", snap_dir)
    assert diff["sections"] == {}


def test_diff_detects_changed_section(snap_dir):
    _write_snap(snap_dir, "snap-001", {"python": "3.10"})
    _write_snap(snap_dir, "snap-002", {"python": "3.11"})
    bl.set_baseline("snap-001", snap_dir)
    diff = bl.diff_against_baseline("snap-002", snap_dir)
    assert "python" in diff["sections"]
    assert diff["sections"]["python"]["baseline"] == "3.10"
    assert diff["sections"]["python"]["target"] == "3.11"


def test_diff_records_labels(snap_dir):
    _write_snap(snap_dir, "snap-001", {"python": "3.10"})
    _write_snap(snap_dir, "snap-002", {"python": "3.11"})
    bl.set_baseline("snap-001", snap_dir)
    diff = bl.diff_against_baseline("snap-002", snap_dir)
    assert diff["baseline"] == "snap-001"
    assert diff["target"] == "snap-002"
