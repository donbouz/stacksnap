"""Tests for stacksnap.archive module."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from stacksnap.archive import (
    archive_snapshots,
    get_snapshot_age_days,
    list_archivable,
    purge_archive,
)


def _write_snap(directory: Path, name: str, age_days: int, pinned: bool = False) -> Path:
    ts = (datetime.utcnow() - timedelta(days=age_days)).isoformat()
    snap = {"name": name, "timestamp": ts, "python": {"version": "3.11.0"}}
    path = directory / f"{name}.json"
    path.write_text(json.dumps(snap))
    return path


@pytest.fixture()
def snap_dir(tmp_path: Path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture()
def archive_dir(tmp_path: Path):
    d = tmp_path / "archive"
    d.mkdir()
    return d


def test_get_snapshot_age_days_recent():
    snap = {"timestamp": datetime.utcnow().isoformat()}
    assert get_snapshot_age_days(snap) < 1


def test_get_snapshot_age_days_old():
    ts = (datetime.utcnow() - timedelta(days=40)).isoformat()
    snap = {"timestamp": ts}
    assert get_snapshot_age_days(snap) >= 40


def test_get_snapshot_age_days_missing_timestamp():
    assert get_snapshot_age_days({}) == float("inf")


def test_list_archivable_returns_old_snaps(snap_dir, monkeypatch):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: False)
    _write_snap(snap_dir, "old-snap", age_days=45)
    _write_snap(snap_dir, "new-snap", age_days=5)
    result = list_archivable(snap_dir, max_age_days=30, keep_pinned=True)
    names = [p.stem for p in result]
    assert "old-snap" in names
    assert "new-snap" not in names


def test_list_archivable_skips_pinned(snap_dir, monkeypatch):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: name == "pinned-old")
    _write_snap(snap_dir, "pinned-old", age_days=60)
    _write_snap(snap_dir, "unpinned-old", age_days=60)
    result = list_archivable(snap_dir, max_age_days=30, keep_pinned=True)
    names = [p.stem for p in result]
    assert "pinned-old" not in names
    assert "unpinned-old" in names


def test_archive_snapshots_moves_files(snap_dir, archive_dir, monkeypatch):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: False)
    _write_snap(snap_dir, "old", age_days=50)
    archived = archive_snapshots(snap_dir, archive_dir, max_age_days=30)
    assert "old" in archived
    assert not (snap_dir / "old.json").exists()
    assert (archive_dir / "old.json").exists()


def test_archive_snapshots_empty_when_nothing_old(snap_dir, archive_dir, monkeypatch):
    monkeypatch.setattr("stacksnap.archive.is_pinned", lambda name, base: False)
    _write_snap(snap_dir, "recent", age_days=2)
    archived = archive_snapshots(snap_dir, archive_dir, max_age_days=30)
    assert archived == []


def test_purge_archive_deletes_old(archive_dir):
    _write_snap(archive_dir, "very-old", age_days=100)
    _write_snap(archive_dir, "medium", age_days=50)
    purged = purge_archive(archive_dir, older_than_days=90)
    assert "very-old" in purged
    assert "medium" not in purged
    assert not (archive_dir / "very-old.json").exists()
    assert (archive_dir / "medium.json").exists()


def test_purge_archive_missing_dir_returns_empty(tmp_path):
    result = purge_archive(archive_dir=tmp_path / "nonexistent", older_than_days=30)
    assert result == []
