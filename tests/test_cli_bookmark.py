"""Tests for stacksnap.cli_bookmark."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from stacksnap.bookmark import set_bookmark
from stacksnap.cli_bookmark import (
    cmd_bookmark_list,
    cmd_bookmark_remove,
    cmd_bookmark_resolve,
    cmd_bookmark_set,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _ns(snap_dir: Path, **kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snap_dir), **kwargs)


def test_cmd_bookmark_set_prints_created(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cmd_bookmark_set(_ns(snap_dir, name="mybm", snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "Created" in out
    assert "mybm" in out


def test_cmd_bookmark_set_prints_updated(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    set_bookmark(snap_dir, "mybm", "snap-001")
    cmd_bookmark_set(_ns(snap_dir, name="mybm", snapshot_id="snap-002"))
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_bookmark_remove_success(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    set_bookmark(snap_dir, "bm", "snap-001")
    cmd_bookmark_remove(_ns(snap_dir, name="bm"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_bookmark_remove_missing(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cmd_bookmark_remove(_ns(snap_dir, name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_bookmark_resolve_prints_id(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    set_bookmark(snap_dir, "bm", "snap-xyz")
    cmd_bookmark_resolve(_ns(snap_dir, name="bm"))
    out = capsys.readouterr().out
    assert "snap-xyz" in out


def test_cmd_bookmark_resolve_missing(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cmd_bookmark_resolve(_ns(snap_dir, name="ghost"))
    out = capsys.readouterr().out
    assert "No bookmark" in out


def test_cmd_bookmark_list_empty(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cmd_bookmark_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "No bookmarks" in out


def test_cmd_bookmark_list_shows_entries(snap_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    set_bookmark(snap_dir, "alpha", "snap-a")
    set_bookmark(snap_dir, "beta", "snap-b")
    cmd_bookmark_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "snap-a" in out
    assert "beta" in out
