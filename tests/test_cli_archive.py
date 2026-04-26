"""Tests for stacksnap.cli_archive module."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from stacksnap.cli_archive import cmd_archive, cmd_purge


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "snapshot_dir": None,
        "archive_dir": None,
        "max_age_days": 30,
        "include_pinned": False,
        "older_than_days": 90,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _write_snap(directory: Path, name: str, age_days: int) -> None:
    ts = (datetime.utcnow() - timedelta(days=age_days)).isoformat()
    snap = {"name": name, "timestamp": ts}
    (directory / f"{name}.json").write_text(json.dumps(snap))


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture()
def arch_dir(tmp_path):
    d = tmp_path / "archive"
    d.mkdir()
    return d


def test_cmd_archive_prints_archived_names(snap_dir, arch_dir, monkeypatch, capsys):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: False)
    _write_snap(snap_dir, "old-proj", 45)
    ns = _ns(snapshot_dir=str(snap_dir), archive_dir=str(arch_dir), max_age_days=30)
    cmd_archive(ns)
    out = capsys.readouterr().out
    assert "old-proj" in out
    assert "Archived" in out


def test_cmd_archive_prints_nothing_eligible(snap_dir, arch_dir, monkeypatch, capsys):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: False)
    _write_snap(snap_dir, "fresh", 2)
    ns = _ns(snapshot_dir=str(snap_dir), archive_dir=str(arch_dir), max_age_days=30)
    cmd_archive(ns)
    out = capsys.readouterr().out
    assert "No snapshots eligible" in out


def test_cmd_purge_prints_purged_names(arch_dir, capsys):
    _write_snap(arch_dir, "ancient", 120)
    ns = _ns(archive_dir=str(arch_dir), older_than_days=90)
    cmd_purge(ns)
    out = capsys.readouterr().out
    assert "ancient" in out
    assert "Purged" in out


def test_cmd_purge_prints_nothing_to_purge(arch_dir, capsys):
    _write_snap(arch_dir, "recent-archive", 10)
    ns = _ns(archive_dir=str(arch_dir), older_than_days=90)
    cmd_purge(ns)
    out = capsys.readouterr().out
    assert "Nothing to purge" in out
