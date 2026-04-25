"""Tests for stacksnap.pin and stacksnap.cli_pin."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from stacksnap.pin import (
    pin_snapshot,
    unpin_snapshot,
    is_pinned,
    list_pinned,
)
from stacksnap.cli_pin import cmd_pin, cmd_unpin, cmd_pin_list, cmd_pin_check


@pytest.fixture()
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path


def _ns(pin_dir: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(snapshot_dir=str(pin_dir), **kwargs)


# --- unit tests for pin module ---

def test_pin_snapshot_returns_true_when_new(pin_dir):
    assert pin_snapshot(pin_dir, "snap-1") is True


def test_pin_snapshot_returns_false_when_duplicate(pin_dir):
    pin_snapshot(pin_dir, "snap-1")
    assert pin_snapshot(pin_dir, "snap-1") is False


def test_pin_snapshot_persists(pin_dir):
    pin_snapshot(pin_dir, "snap-2")
    assert is_pinned(pin_dir, "snap-2") is True


def test_unpin_snapshot_returns_true_when_present(pin_dir):
    pin_snapshot(pin_dir, "snap-3")
    assert unpin_snapshot(pin_dir, "snap-3") is True


def test_unpin_snapshot_returns_false_when_absent(pin_dir):
    assert unpin_snapshot(pin_dir, "ghost") is False


def test_is_pinned_false_before_pinning(pin_dir):
    assert is_pinned(pin_dir, "snap-x") is False


def test_list_pinned_empty_initially(pin_dir):
    assert list_pinned(pin_dir) == []


def test_list_pinned_returns_all(pin_dir):
    pin_snapshot(pin_dir, "a")
    pin_snapshot(pin_dir, "b")
    pins = list_pinned(pin_dir)
    assert set(pins) == {"a", "b"}


def test_unpin_removes_from_list(pin_dir):
    pin_snapshot(pin_dir, "a")
    pin_snapshot(pin_dir, "b")
    unpin_snapshot(pin_dir, "a")
    assert list_pinned(pin_dir) == ["b"]


# --- CLI command tests ---

def test_cmd_pin_prints_confirmation(pin_dir, capsys):
    cmd_pin(_ns(pin_dir, label="snap-1"))
    out = capsys.readouterr().out
    assert "Pinned" in out and "snap-1" in out


def test_cmd_pin_prints_already_pinned(pin_dir, capsys):
    pin_snapshot(pin_dir, "snap-1")
    cmd_pin(_ns(pin_dir, label="snap-1"))
    out = capsys.readouterr().out
    assert "already pinned" in out


def test_cmd_unpin_success(pin_dir, capsys):
    pin_snapshot(pin_dir, "snap-2")
    cmd_unpin(_ns(pin_dir, label="snap-2"))
    out = capsys.readouterr().out
    assert "Unpinned" in out


def test_cmd_unpin_not_pinned(pin_dir, capsys):
    cmd_unpin(_ns(pin_dir, label="ghost"))
    out = capsys.readouterr().out
    assert "not pinned" in out


def test_cmd_pin_list_empty(pin_dir, capsys):
    cmd_pin_list(_ns(pin_dir))
    out = capsys.readouterr().out
    assert "No pinned" in out


def test_cmd_pin_list_shows_labels(pin_dir, capsys):
    pin_snapshot(pin_dir, "alpha")
    cmd_pin_list(_ns(pin_dir))
    out = capsys.readouterr().out
    assert "alpha" in out


def test_cmd_pin_check_pinned(pin_dir, capsys):
    pin_snapshot(pin_dir, "snap-z")
    cmd_pin_check(_ns(pin_dir, label="snap-z"))
    assert "pinned" in capsys.readouterr().out


def test_cmd_pin_check_not_pinned(pin_dir, capsys):
    cmd_pin_check(_ns(pin_dir, label="snap-z"))
    assert "not pinned" in capsys.readouterr().out
