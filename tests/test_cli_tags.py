"""Tests for stacksnap/cli_tags.py"""

import pytest
from pathlib import Path
from unittest.mock import patch

from stacksnap.cli_tags import (
    cmd_tag_add,
    cmd_tag_remove,
    cmd_tag_list,
    cmd_tag_find,
)
from stacksnap.tags import add_tag


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path


def _ns(snap_dir, **kwargs):
    """Build a minimal argparse.Namespace for tag commands."""
    import argparse
    defaults = {"snapshot_dir": str(snap_dir)}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_tag_add_prints_confirmation(snap_dir, capsys):
    args = _ns(snap_dir, snapshot="snap-1", tag="stable")
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "stable" in out


def test_cmd_tag_remove_success(snap_dir, capsys):
    add_tag(snap_dir, "snap-1", "stable")
    args = _ns(snap_dir, snapshot="snap-1", tag="stable")
    cmd_tag_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_tag_remove_missing_tag(snap_dir, capsys):
    args = _ns(snap_dir, snapshot="snap-1", tag="ghost")
    cmd_tag_remove(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_tag_list_specific_snapshot(snap_dir, capsys):
    add_tag(snap_dir, "snap-1", "prod")
    args = _ns(snap_dir, snapshot="snap-1")
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_tag_list_no_tags_message(snap_dir, capsys):
    args = _ns(snap_dir, snapshot="snap-empty")
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_list_all(snap_dir, capsys):
    add_tag(snap_dir, "snap-1", "stable")
    add_tag(snap_dir, "snap-2", "dev")
    args = _ns(snap_dir, snapshot=None)
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "snap-2" in out


def test_cmd_tag_list_all_empty(snap_dir, capsys):
    args = _ns(snap_dir, snapshot=None)
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_find_matches(snap_dir, capsys):
    add_tag(snap_dir, "snap-1", "stable")
    add_tag(snap_dir, "snap-2", "dev")
    args = _ns(snap_dir, tag="stable")
    cmd_tag_find(args)
    out = capsys.readouterr().out
    assert "snap-1" in out
    assert "snap-2" not in out


def test_cmd_tag_find_no_matches(snap_dir, capsys):
    args = _ns(snap_dir, tag="nonexistent")
    cmd_tag_find(args)
    out = capsys.readouterr().out
    assert "No snapshots" in out
