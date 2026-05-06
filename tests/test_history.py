"""Tests for stacksnap.history and stacksnap.cli_history."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.history import (
    clear_history,
    get_history,
    most_accessed,
    record_access,
)
from stacksnap.cli_history import (
    build_history_parser,
    cmd_history_clear,
    cmd_history_log,
    cmd_history_record,
    cmd_history_top,
)


@pytest.fixture()
def hist_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _ns(hist_dir: Path, **kwargs):
    import argparse
    ns = argparse.Namespace(snapshot_dir=str(hist_dir), **kwargs)
    return ns


# --- unit tests for history module ---

def test_record_access_returns_entry(hist_dir):
    entry = record_access(hist_dir, "snap-001")
    assert entry["snapshot_id"] == "snap-001"
    assert entry["action"] == "view"
    assert "timestamp" in entry


def test_record_access_persists(hist_dir):
    record_access(hist_dir, "snap-001", action="restore")
    data = json.loads((hist_dir / "history.json").read_text())
    assert len(data) == 1
    assert data[0]["action"] == "restore"


def test_record_access_empty_id_raises(hist_dir):
    with pytest.raises(ValueError):
        record_access(hist_dir, "")


def test_get_history_returns_all(hist_dir):
    record_access(hist_dir, "a")
    record_access(hist_dir, "b")
    assert len(get_history(hist_dir)) == 2


def test_get_history_filter_by_id(hist_dir):
    record_access(hist_dir, "a")
    record_access(hist_dir, "b")
    result = get_history(hist_dir, snapshot_id="a")
    assert all(e["snapshot_id"] == "a" for e in result)


def test_get_history_filter_by_action(hist_dir):
    record_access(hist_dir, "a", action="view")
    record_access(hist_dir, "a", action="restore")
    result = get_history(hist_dir, action="restore")
    assert len(result) == 1


def test_get_history_limit(hist_dir):
    for i in range(10):
        record_access(hist_dir, f"snap-{i}")
    result = get_history(hist_dir, limit=3)
    assert len(result) == 3


def test_clear_history_all(hist_dir):
    record_access(hist_dir, "a")
    record_access(hist_dir, "b")
    removed = clear_history(hist_dir)
    assert removed == 2
    assert get_history(hist_dir) == []


def test_clear_history_by_id(hist_dir):
    record_access(hist_dir, "a")
    record_access(hist_dir, "b")
    removed = clear_history(hist_dir, snapshot_id="a")
    assert removed == 1
    remaining = get_history(hist_dir)
    assert all(e["snapshot_id"] == "b" for e in remaining)


def test_most_accessed_order(hist_dir):
    for _ in range(3):
        record_access(hist_dir, "popular")
    record_access(hist_dir, "rare")
    top = most_accessed(hist_dir, top_n=2)
    assert top[0][0] == "popular"
    assert top[0][1] == 3


# --- CLI command tests ---

def test_cmd_history_record_prints_confirmation(hist_dir, capsys):
    cmd_history_record(_ns(hist_dir, id="snap-x", action="view"))
    out = capsys.readouterr().out
    assert "snap-x" in out
    assert "view" in out


def test_cmd_history_log_prints_entries(hist_dir, capsys):
    record_access(hist_dir, "snap-y", action="restore")
    cmd_history_log(_ns(hist_dir, id=None, action=None, limit=None))
    out = capsys.readouterr().out
    assert "snap-y" in out


def test_cmd_history_log_empty(hist_dir, capsys):
    cmd_history_log(_ns(hist_dir, id=None, action=None, limit=None))
    out = capsys.readouterr().out
    assert "No history" in out


def test_cmd_history_clear_prints_count(hist_dir, capsys):
    record_access(hist_dir, "snap-z")
    cmd_history_clear(_ns(hist_dir, id=None))
    out = capsys.readouterr().out
    assert "1" in out


def test_cmd_history_top_prints_ranking(hist_dir, capsys):
    record_access(hist_dir, "snap-a")
    record_access(hist_dir, "snap-a")
    record_access(hist_dir, "snap-b")
    cmd_history_top(_ns(hist_dir, top=5))
    out = capsys.readouterr().out
    assert "snap-a" in out
    lines = [l for l in out.strip().splitlines() if l]
    assert lines[0].startswith("1.")


def test_build_history_parser_returns_parser(hist_dir):
    parser = build_history_parser(snapshot_dir=str(hist_dir))
    assert parser is not None
