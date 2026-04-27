"""Tests for stacksnap.cli_alias."""

import argparse
import pytest
from pathlib import Path

from stacksnap.alias import set_alias
from stacksnap.cli_alias import (
    cmd_alias_set,
    cmd_alias_remove,
    cmd_alias_resolve,
    cmd_alias_list,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _ns(snap_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=snap_dir, **kwargs)


def test_cmd_alias_set_prints_created(snap_dir, capsys):
    cmd_alias_set(_ns(snap_dir, alias="prod", snapshot_id="snap-001"))
    out = capsys.readouterr().out
    assert "Created" in out
    assert "prod" in out


def test_cmd_alias_set_prints_updated(snap_dir, capsys):
    set_alias(snap_dir, "prod", "snap-001")
    cmd_alias_set(_ns(snap_dir, alias="prod", snapshot_id="snap-002"))
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_alias_remove_success(snap_dir, capsys):
    set_alias(snap_dir, "dev", "snap-003")
    cmd_alias_remove(_ns(snap_dir, alias="dev"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_alias_remove_missing(snap_dir, capsys):
    cmd_alias_remove(_ns(snap_dir, alias="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_alias_resolve_found(snap_dir, capsys):
    set_alias(snap_dir, "staging", "snap-010")
    cmd_alias_resolve(_ns(snap_dir, alias="staging"))
    out = capsys.readouterr().out
    assert "snap-010" in out


def test_cmd_alias_resolve_not_found(snap_dir, capsys):
    cmd_alias_resolve(_ns(snap_dir, alias="unknown"))
    out = capsys.readouterr().out
    assert "No alias" in out


def test_cmd_alias_list_empty(snap_dir, capsys):
    cmd_alias_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_list_shows_entries(snap_dir, capsys):
    set_alias(snap_dir, "alpha", "snap-A")
    set_alias(snap_dir, "beta", "snap-B")
    cmd_alias_list(_ns(snap_dir))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "snap-A" in out
    assert "beta" in out
