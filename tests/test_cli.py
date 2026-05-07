"""Tests for CLI capture command: --strict, --verbose, and skipped-file warnings."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from stacksnap.cli import build_parser, cmd_capture


@pytest.fixture()
def snap_with_skipped(tmp_path):
    return {
        "label": "test-snap",
        "timestamp": "2026-01-01T00:00:00",
        "cwd": str(tmp_path),
        "python_version": "",
        "node_version": "",
        "git_branch": "",
        "git_commit": "",
        "pip_packages": "",
        "env_vars": {},
        "files": {},
        "skipped_files": ["secret.env"],
    }


@pytest.fixture()
def snap_clean(tmp_path):
    return {
        "label": "test-snap",
        "timestamp": "2026-01-01T00:00:00",
        "cwd": str(tmp_path),
        "python_version": "",
        "node_version": "",
        "git_branch": "",
        "git_commit": "",
        "pip_packages": "",
        "env_vars": {},
        "files": {},
        "skipped_files": [],
    }


def _make_args(tmp_path, strict=False, verbose=False):
    parser = build_parser()
    args = parser.parse_args(["capture"])
    args.snapshot_dir = tmp_path / "snapshots"
    args.strict = strict
    args.verbose = verbose
    args.name = "test-snap"
    return args


def test_cmd_capture_no_warning_when_no_skipped(tmp_path, snap_clean, capsys):
    with patch("stacksnap.cli.capture_snapshot", return_value=snap_clean), \
         patch("stacksnap.cli.save_snapshot", return_value=tmp_path / "test-snap.json"):
        cmd_capture(_make_args(tmp_path))
    captured = capsys.readouterr()
    assert "WARNING" not in captured.err


def test_cmd_capture_warns_on_skipped_files(tmp_path, snap_with_skipped, capsys):
    with patch("stacksnap.cli.capture_snapshot", return_value=snap_with_skipped), \
         patch("stacksnap.cli.save_snapshot", return_value=tmp_path / "test-snap.json"):
        cmd_capture(_make_args(tmp_path))
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "1 unreadable file" in captured.err
    assert "secret.env" not in captured.err  # not listed without --verbose


def test_cmd_capture_verbose_lists_skipped_paths(tmp_path, snap_with_skipped, capsys):
    with patch("stacksnap.cli.capture_snapshot", return_value=snap_with_skipped), \
         patch("stacksnap.cli.save_snapshot", return_value=tmp_path / "test-snap.json"):
        cmd_capture(_make_args(tmp_path, verbose=True))
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "secret.env" in captured.err


def test_cmd_capture_strict_exits_nonzero(tmp_path, snap_with_skipped):
    with patch("stacksnap.cli.capture_snapshot", return_value=snap_with_skipped), \
         patch("stacksnap.cli.save_snapshot", return_value=tmp_path / "test-snap.json"), \
         pytest.raises(SystemExit) as exc_info:
        cmd_capture(_make_args(tmp_path, strict=True))
    assert exc_info.value.code == 1


def test_cmd_capture_strict_no_exit_when_no_skipped(tmp_path, snap_clean):
    with patch("stacksnap.cli.capture_snapshot", return_value=snap_clean), \
         patch("stacksnap.cli.save_snapshot", return_value=tmp_path / "test-snap.json"):
        cmd_capture(_make_args(tmp_path, strict=True))  # should not raise
