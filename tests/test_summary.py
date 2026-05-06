"""Tests for stacksnap.summary and stacksnap.cli_summary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.summary import summarise_snapshot, format_summary, summarise_snapshot_file
from stacksnap.cli_summary import cmd_summary, build_summary_parser


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture()
def full_snapshot() -> dict:
    return {
        "label": "my-feature",
        "captured_at": "2024-06-01T12:00:00",
        "python": {"version": "3.11.4", "virtualenv": "/home/user/.venvs/proj"},
        "node": {"version": "20.3.0"},
        "env_vars": {"DEBUG": "1", "PORT": "8080"},
        "git": {"branch": "main", "commit": "abc1234"},
    }


def test_summarise_snapshot_extracts_label(full_snapshot):
    result = summarise_snapshot(full_snapshot)
    assert result["label"] == "my-feature"


def test_summarise_snapshot_extracts_python_version(full_snapshot):
    result = summarise_snapshot(full_snapshot)
    assert result["python_version"] == "3.11.4"


def test_summarise_snapshot_extracts_node_version(full_snapshot):
    result = summarise_snapshot(full_snapshot)
    assert result["node_version"] == "20.3.0"


def test_summarise_snapshot_counts_env_vars(full_snapshot):
    result = summarise_snapshot(full_snapshot)
    assert result["env_var_count"] == 2


def test_summarise_snapshot_extracts_git_info(full_snapshot):
    result = summarise_snapshot(full_snapshot)
    assert result["git_branch"] == "main"
    assert result["git_commit"] == "abc1234"


def test_summarise_snapshot_defaults_for_missing_sections():
    result = summarise_snapshot({})
    assert result["label"] == "<unlabelled>"
    assert result["python_version"] == "n/a"
    assert result["node_version"] == "n/a"
    assert result["env_var_count"] == 0
    assert result["virtualenv"] == "none"


def test_format_summary_contains_label(full_snapshot):
    summary = summarise_snapshot(full_snapshot)
    text = format_summary(summary)
    assert "my-feature" in text


def test_format_summary_contains_python_version(full_snapshot):
    summary = summarise_snapshot(full_snapshot)
    text = format_summary(summary)
    assert "3.11.4" in text


def test_format_summary_contains_separator_line(full_snapshot):
    summary = summarise_snapshot(full_snapshot)
    text = format_summary(summary)
    assert "---" in text


def test_summarise_snapshot_file_reads_json(snap_dir, full_snapshot):
    snap_file = snap_dir / "my-feature.json"
    snap_file.write_text(json.dumps(full_snapshot))
    text = summarise_snapshot_file(snap_file)
    assert "my-feature" in text


def test_summarise_snapshot_file_raises_for_missing(snap_dir):
    with pytest.raises(FileNotFoundError):
        summarise_snapshot_file(snap_dir / "ghost.json")


def _ns(snap_dir: Path, name: str, **kwargs) -> object:
    import argparse
    ns = argparse.Namespace(name=name, snapshot_dir=str(snap_dir), **kwargs)
    return ns


def test_cmd_summary_prints_output(snap_dir, full_snapshot, capsys):
    (snap_dir / "my-feature.json").write_text(json.dumps(full_snapshot))
    cmd_summary(_ns(snap_dir, "my-feature"))
    out = capsys.readouterr().out
    assert "my-feature" in out
    assert "3.11.4" in out


def test_cmd_summary_prints_error_for_missing(snap_dir, capsys):
    cmd_summary(_ns(snap_dir, "ghost"))
    out = capsys.readouterr().out
    assert "[error]" in out
    assert "ghost" in out


def test_build_summary_parser_returns_parser():
    parser = build_summary_parser()
    args = parser.parse_args(["my-snap"])
    assert args.name == "my-snap"
