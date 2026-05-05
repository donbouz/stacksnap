"""Tests for stacksnap.replay."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.replay import build_replay_script, replay_snapshot


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

SAMPLE_SNAPSHOT = {
    "label": "my-project-2024",
    "python": {"version": "3.11.4", "virtualenv": "/home/user/.venvs/myproject"},
    "node": {"version": "20.11.0"},
    "env_vars": {"DEBUG": "true", "DATABASE_URL": "postgres://localhost/mydb"},
}


@pytest.fixture()
def snap_file(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(SAMPLE_SNAPSHOT))
    return p


# ---------------------------------------------------------------------------
# build_replay_script
# ---------------------------------------------------------------------------


def test_script_contains_shebang():
    script = build_replay_script(SAMPLE_SNAPSHOT)
    assert script.startswith("#!/usr/bin/env sh")


def test_script_exports_env_vars():
    script = build_replay_script(SAMPLE_SNAPSHOT)
    assert "export DEBUG='true'" in script or 'export DEBUG=true' in script
    assert "DATABASE_URL" in script


def test_script_sources_virtualenv():
    script = build_replay_script(SAMPLE_SNAPSHOT)
    assert "/home/user/.venvs/myproject" in script
    assert ". " in script  # source command present


def test_script_includes_nvm_when_node_present():
    script = build_replay_script(SAMPLE_SNAPSHOT, include_node=True)
    assert "nvm use" in script
    assert "20.11.0" in script


def test_script_omits_nvm_when_include_node_false():
    script = build_replay_script(SAMPLE_SNAPSHOT, include_node=False)
    assert "nvm" not in script


def test_script_contains_label():
    script = build_replay_script(SAMPLE_SNAPSHOT)
    assert "my-project-2024" in script


def test_script_no_env_vars_section_when_empty():
    snap = {**SAMPLE_SNAPSHOT, "env_vars": {}}
    script = build_replay_script(snap)
    assert "export" not in script


def test_script_no_virtualenv_section_when_missing():
    snap = {**SAMPLE_SNAPSHOT, "python": {"version": "3.11.4"}}
    script = build_replay_script(snap)
    assert "activate" not in script


def test_script_no_node_section_when_missing():
    snap = {**SAMPLE_SNAPSHOT, "node": {}}
    script = build_replay_script(snap)
    assert "nvm" not in script


# ---------------------------------------------------------------------------
# replay_snapshot
# ---------------------------------------------------------------------------


def test_replay_snapshot_returns_script_when_no_output(snap_file: Path):
    result = replay_snapshot(snap_file)
    assert isinstance(result, str)
    assert "my-project-2024" in result


def test_replay_snapshot_writes_file(tmp_path: Path, snap_file: Path):
    out = tmp_path / "replay.sh"
    returned = replay_snapshot(snap_file, out)
    assert returned == str(out)
    assert out.exists()
    assert "my-project-2024" in out.read_text()


def test_replay_snapshot_file_is_executable(tmp_path: Path, snap_file: Path):
    out = tmp_path / "replay.sh"
    replay_snapshot(snap_file, out)
    assert out.stat().st_mode & 0o111  # at least one execute bit set
