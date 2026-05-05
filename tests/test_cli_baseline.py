"""Tests for stacksnap/cli_baseline.py"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from stacksnap import baseline as bl
from stacksnap.cli_baseline import (
    cmd_baseline_clear,
    cmd_baseline_diff,
    cmd_baseline_get,
    cmd_baseline_set,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _ns(snap_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snap_dir), **kwargs)


def _write_snap(snap_dir: Path, snap_id: str, data: dict) -> None:
    (snap_dir / f"{snap_id}.json").write_text(json.dumps(data), encoding="utf-8")


def test_cmd_baseline_set_prints_set(snap_dir, capsys):
    cmd_baseline_set(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "snap-001" in out
    assert "set" in out.lower()


def test_cmd_baseline_set_prints_already(snap_dir, capsys):
    bl.set_baseline("snap-001", snap_dir)
    cmd_baseline_set(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "already" in out.lower()


def test_cmd_baseline_get_shows_current(snap_dir, capsys):
    bl.set_baseline("snap-42", snap_dir)
    cmd_baseline_get(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "snap-42" in out


def test_cmd_baseline_get_shows_none(snap_dir, capsys):
    cmd_baseline_get(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "No baseline" in out


def test_cmd_baseline_clear_success(snap_dir, capsys):
    bl.set_baseline("snap-001", snap_dir)
    cmd_baseline_clear(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "cleared" in out.lower()
    assert bl.get_baseline(snap_dir) is None


def test_cmd_baseline_clear_when_not_set(snap_dir, capsys):
    cmd_baseline_clear(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "No baseline" in out


def test_cmd_baseline_diff_no_baseline(snap_dir, capsys):
    _write_snap(snap_dir, "snap-002", {"python": "3.11"})
    cmd_baseline_diff(_ns(snap_dir, snapshot_id="snap-002"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_baseline_diff_no_differences(snap_dir, capsys):
    data = {"python": "3.11"}
    _write_snap(snap_dir, "snap-001", data)
    _write_snap(snap_dir, "snap-002", data)
    bl.set_baseline("snap-001", snap_dir)
    cmd_baseline_diff(_ns(snap_dir, snapshot_id="snap-002"))
    out = capsys.readouterr().out
    assert "No differences" in out


def test_cmd_baseline_diff_shows_changes(snap_dir, capsys):
    _write_snap(snap_dir, "snap-001", {"python": "3.10"})
    _write_snap(snap_dir, "snap-002", {"python": "3.11"})
    bl.set_baseline("snap-001", snap_dir)
    cmd_baseline_diff(_ns(snap_dir, snapshot_id="snap-002"))
    out = capsys.readouterr().out
    assert "python" in out
    assert "3.10" in out
    assert "3.11" in out
