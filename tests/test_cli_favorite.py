"""Tests for stacksnap.cli_favorite."""
from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from stacksnap.favorite import add_favorite
from stacksnap.cli_favorite import (
    cmd_favorite_add,
    cmd_favorite_remove,
    cmd_favorite_list,
    cmd_favorite_check,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _ns(snap_dir: Path, **kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snap_dir), **kwargs)


def test_cmd_favorite_add_prints_starred(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    cmd_favorite_add(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "Starred" in out
    assert "snap-001" in out


def test_cmd_favorite_add_prints_already_starred(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    add_favorite("snap-001", snap_dir)
    cmd_favorite_add(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "already starred" in out


def test_cmd_favorite_remove_success(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    add_favorite("snap-001", snap_dir)
    cmd_favorite_remove(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "Unstarred" in out


def test_cmd_favorite_remove_not_starred(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    cmd_favorite_remove(_ns(snap_dir, snapshot_id="snap-999"))
    out = capsys.readouterr().out
    assert "not starred" in out


def test_cmd_favorite_list_empty(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    cmd_favorite_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "No starred" in out


def test_cmd_favorite_list_shows_entries(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    add_favorite("snap-001", snap_dir)
    add_favorite("snap-002", snap_dir)
    cmd_favorite_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "snap-001" in out
    assert "snap-002" in out


def test_cmd_favorite_check_starred(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    add_favorite("snap-001", snap_dir)
    cmd_favorite_check(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "starred" in out
    assert "not starred" not in out


def test_cmd_favorite_check_not_starred(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    cmd_favorite_check(_ns(snap_dir, snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "not starred" in out
