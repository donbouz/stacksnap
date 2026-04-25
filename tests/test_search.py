"""Tests for stacksnap.search and stacksnap.cli_search."""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from stacksnap.search import format_search_results, search_snapshots
from stacksnap.cli_search import cmd_search


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    """Populate a temporary snapshot directory with two snapshots."""
    d = tmp_path / "snapshots"
    d.mkdir()

    snap_a = {
        "label": "alpha",
        "timestamp": "2024-01-01T00:00:00",
        "python": {"version": "Python 3.11.4"},
        "node": {"version": "v20.1.0"},
        "env": {"MY_VAR": "hello"},
    }
    snap_b = {
        "label": "beta",
        "timestamp": "2024-06-01T00:00:00",
        "python": {"version": "Python 3.9.2"},
        "node": {"version": "v18.0.0"},
        "env": {"OTHER": "world"},
    }
    (d / "alpha.json").write_text(json.dumps(snap_a))
    (d / "beta.json").write_text(json.dumps(snap_b))
    return d


def test_search_no_filters_returns_all(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir)
    assert len(results) == 2


def test_search_by_free_text_matches_label(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, query="alph")
    assert len(results) == 1
    assert results[0]["label"] == "alpha"


def test_search_by_free_text_matches_env_value(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, query="hello")
    assert len(results) == 1
    assert results[0]["label"] == "alpha"


def test_search_by_python_version(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, python_version="3.11")
    assert len(results) == 1
    assert results[0]["label"] == "alpha"


def test_search_by_node_version(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, node_version="18")
    assert len(results) == 1
    assert results[0]["label"] == "beta"


def test_search_no_match_returns_empty(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, query="zzznomatch")
    assert results == []


def test_search_combined_filters(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, query="alpha", python_version="3.11")
    assert len(results) == 1


def test_format_results_empty() -> None:
    output = format_search_results([])
    assert "No snapshots matched" in output


def test_format_results_contains_label(snap_dir: Path) -> None:
    results = search_snapshots(snap_dir, query="beta")
    output = format_search_results(results)
    assert "beta" in output
    assert "3.9" in output


def test_cmd_search_prints_results(snap_dir: Path, capsys: pytest.CaptureFixture) -> None:
    ns = types.SimpleNamespace(
        snapshots_dir=str(snap_dir),
        query="alpha",
        tag="",
        python="",
        node="",
    )
    cmd_search(ns)
    captured = capsys.readouterr()
    assert "alpha" in captured.out


def test_cmd_search_no_match_prints_message(
    snap_dir: Path, capsys: pytest.CaptureFixture
) -> None:
    ns = types.SimpleNamespace(
        snapshots_dir=str(snap_dir),
        query="zzznomatch",
        tag="",
        python="",
        node="",
    )
    cmd_search(ns)
    captured = capsys.readouterr()
    assert "No snapshots matched" in captured.out
