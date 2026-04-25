"""Tests for stacksnap.cli_notes."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from stacksnap.cli_notes import cmd_note_add, cmd_note_list, cmd_note_delete
from stacksnap.notes import add_note


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _ns(snap_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(snap_dir), **kwargs)


def test_cmd_note_add_prints_confirmation(snap_dir, capsys):
    ns = _ns(snap_dir, snapshot_id="s1", text="my note")
    cmd_note_add(ns)
    out = capsys.readouterr().out
    assert "Note added" in out


def test_cmd_note_add_empty_text_raises(snap_dir):
    ns = _ns(snap_dir, snapshot_id="s1", text="")
    with pytest.raises(ValueError):
        cmd_note_add(ns)


def test_cmd_note_list_shows_notes(snap_dir, capsys):
    add_note("s1", "visible note", snap_dir)
    ns = _ns(snap_dir, snapshot_id="s1")
    cmd_note_list(ns)
    out = capsys.readouterr().out
    assert "visible note" in out


def test_cmd_note_list_empty(snap_dir, capsys):
    ns = _ns(snap_dir, snapshot_id="s1")
    cmd_note_list(ns)
    out = capsys.readouterr().out
    assert "No notes" in out


def test_cmd_note_delete_success(snap_dir, capsys):
    add_note("s1", "to delete", snap_dir)
    ns = _ns(snap_dir, snapshot_id="s1")
    cmd_note_delete(ns)
    out = capsys.readouterr().out
    assert "deleted" in out.lower()


def test_cmd_note_delete_missing(snap_dir, capsys):
    ns = _ns(snap_dir, snapshot_id="ghost")
    cmd_note_delete(ns)
    out = capsys.readouterr().out
    assert "No notes found" in out
