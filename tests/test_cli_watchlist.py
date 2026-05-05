"""Tests for stacksnap.cli_watchlist."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from stacksnap.cli_watchlist import (
    cmd_watch_add,
    cmd_watch_check,
    cmd_watch_clear,
    cmd_watch_list,
    cmd_watch_remove,
)
from stacksnap.watchlist import add_to_watchlist


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _ns(snap_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(directory=snap_dir, **kwargs)


def test_cmd_watch_add_prints_watching(snap_dir, capsys):
    cmd_watch_add(_ns(snap_dir, snapshot_id="snap-001", reason=""))
    assert "Watching: snap-001" in capsys.readouterr().out


def test_cmd_watch_add_prints_already_watched(snap_dir, capsys):
    add_to_watchlist(snap_dir, "snap-001")
    cmd_watch_add(_ns(snap_dir, snapshot_id="snap-001", reason=""))
    assert "Already watched" in capsys.readouterr().out


def test_cmd_watch_remove_success(snap_dir, capsys):
    add_to_watchlist(snap_dir, "snap-002")
    cmd_watch_remove(_ns(snap_dir, snapshot_id="snap-002"))
    assert "Removed" in capsys.readouterr().out


def test_cmd_watch_remove_missing(snap_dir, capsys):
    cmd_watch_remove(_ns(snap_dir, snapshot_id="snap-999"))
    assert "Not in watchlist" in capsys.readouterr().out


def test_cmd_watch_list_empty(snap_dir, capsys):
    cmd_watch_list(_ns(snap_dir))
    assert "empty" in capsys.readouterr().out


def test_cmd_watch_list_shows_entries(snap_dir, capsys):
    add_to_watchlist(snap_dir, "snap-010", reason="prod baseline")
    cmd_watch_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "snap-010" in out
    assert "prod baseline" in out


def test_cmd_watch_check_watched(snap_dir, capsys):
    add_to_watchlist(snap_dir, "snap-020")
    cmd_watch_check(_ns(snap_dir, snapshot_id="snap-020"))
    assert "watched" in capsys.readouterr().out


def test_cmd_watch_check_not_watched(snap_dir, capsys):
    cmd_watch_check(_ns(snap_dir, snapshot_id="snap-030"))
    assert "not watched" in capsys.readouterr().out


def test_cmd_watch_clear_reports_count(snap_dir, capsys):
    add_to_watchlist(snap_dir, "snap-040")
    add_to_watchlist(snap_dir, "snap-041")
    cmd_watch_clear(_ns(snap_dir))
    assert "2" in capsys.readouterr().out


def test_cmd_watch_clear_empty(snap_dir, capsys):
    cmd_watch_clear(_ns(snap_dir))
    assert "0" in capsys.readouterr().out
