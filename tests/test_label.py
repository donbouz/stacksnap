"""Tests for stacksnap.label and stacksnap.cli_label."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.label import relabel_snapshot, rename_snapshot
from stacksnap.cli_label import cmd_relabel, cmd_rename


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_snap(directory: Path, name: str, label: str | None = None) -> Path:
    path = directory / f"{name}.json"
    payload = {"label": label or name, "python": {"version": "3.11.0"}, "node": {}, "env_vars": {}}
    path.write_text(json.dumps(payload))
    return path


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _ns(**kwargs):
    import argparse
    ns = argparse.Namespace(**kwargs)
    return ns


# ---------------------------------------------------------------------------
# rename_snapshot
# ---------------------------------------------------------------------------


def test_rename_moves_file(snap_dir):
    _write_snap(snap_dir, "alpha")
    result = rename_snapshot(snap_dir, "alpha", "beta")
    assert result["ok"] is True
    assert (snap_dir / "beta.json").exists()
    assert not (snap_dir / "alpha.json").exists()


def test_rename_updates_embedded_label(snap_dir):
    _write_snap(snap_dir, "alpha")
    rename_snapshot(snap_dir, "alpha", "beta")
    data = json.loads((snap_dir / "beta.json").read_text())
    assert data["label"] == "beta"


def test_rename_missing_source_returns_error(snap_dir):
    result = rename_snapshot(snap_dir, "ghost", "phantom")
    assert result["ok"] is False
    assert "not found" in result["reason"]


def test_rename_empty_new_name_returns_error(snap_dir):
    _write_snap(snap_dir, "alpha")
    result = rename_snapshot(snap_dir, "alpha", "   ")
    assert result["ok"] is False
    assert "empty" in result["reason"]


def test_rename_refuses_overwrite_by_default(snap_dir):
    _write_snap(snap_dir, "alpha")
    _write_snap(snap_dir, "beta")
    result = rename_snapshot(snap_dir, "alpha", "beta")
    assert result["ok"] is False
    assert "already exists" in result["reason"]


def test_rename_allows_overwrite_when_flag_set(snap_dir):
    _write_snap(snap_dir, "alpha", label="Alpha Label")
    _write_snap(snap_dir, "beta", label="Old Beta")
    result = rename_snapshot(snap_dir, "alpha", "beta", overwrite=True)
    assert result["ok"] is True
    data = json.loads((snap_dir / "beta.json").read_text())
    assert data["label"] == "beta"


# ---------------------------------------------------------------------------
# relabel_snapshot
# ---------------------------------------------------------------------------


def test_relabel_updates_label_field(snap_dir):
    _write_snap(snap_dir, "mysnap", label="Old Label")
    result = relabel_snapshot(snap_dir, "mysnap", "New Label")
    assert result["ok"] is True
    data = json.loads((snap_dir / "mysnap.json").read_text())
    assert data["label"] == "New Label"


def test_relabel_file_name_unchanged(snap_dir):
    _write_snap(snap_dir, "mysnap")
    relabel_snapshot(snap_dir, "mysnap", "Shiny New Label")
    assert (snap_dir / "mysnap.json").exists()


def test_relabel_missing_snapshot_returns_error(snap_dir):
    result = relabel_snapshot(snap_dir, "nope", "Whatever")
    assert result["ok"] is False
    assert "not found" in result["reason"]


def test_relabel_empty_label_returns_error(snap_dir):
    _write_snap(snap_dir, "mysnap")
    result = relabel_snapshot(snap_dir, "mysnap", "")
    assert result["ok"] is False
    assert "empty" in result["reason"]


def test_relabel_returns_old_label(snap_dir):
    _write_snap(snap_dir, "mysnap", label="Original")
    result = relabel_snapshot(snap_dir, "mysnap", "Updated")
    assert result["old_label"] == "Original"


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def test_cmd_rename_prints_confirmation(snap_dir, capsys):
    _write_snap(snap_dir, "alpha")
    cmd_rename(_ns(old_name="alpha", new_name="gamma", overwrite=False, snapshot_dir=str(snap_dir)))
    out = capsys.readouterr().out
    assert "alpha" in out and "gamma" in out


def test_cmd_rename_prints_error_on_missing(snap_dir, capsys):
    cmd_rename(_ns(old_name="ghost", new_name="gamma", overwrite=False, snapshot_dir=str(snap_dir)))
    out = capsys.readouterr().out
    assert "error" in out


def test_cmd_relabel_prints_confirmation(snap_dir, capsys):
    _write_snap(snap_dir, "mysnap", label="Old")
    cmd_relabel(_ns(name="mysnap", label="New Label", snapshot_dir=str(snap_dir)))
    out = capsys.readouterr().out
    assert "Old" in out
    assert "New Label" in out
