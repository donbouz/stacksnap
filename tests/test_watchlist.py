"""Tests for stacksnap.watchlist."""

from __future__ import annotations

import pytest
from pathlib import Path

from stacksnap.watchlist import (
    add_to_watchlist,
    clear_watchlist,
    get_watchlist,
    is_watched,
    remove_from_watchlist,
)


@pytest.fixture()
def watch_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_add_returns_true_when_new(watch_dir):
    assert add_to_watchlist(watch_dir, "snap-001") is True


def test_add_returns_false_when_duplicate(watch_dir):
    add_to_watchlist(watch_dir, "snap-001")
    assert add_to_watchlist(watch_dir, "snap-001") is False


def test_add_persists(watch_dir):
    add_to_watchlist(watch_dir, "snap-002", reason="important")
    data = get_watchlist(watch_dir)
    assert "snap-002" in data


def test_add_stores_reason(watch_dir):
    add_to_watchlist(watch_dir, "snap-003", reason="baseline")
    data = get_watchlist(watch_dir)
    assert data["snap-003"]["reason"] == "baseline"


def test_add_empty_id_raises(watch_dir):
    with pytest.raises(ValueError):
        add_to_watchlist(watch_dir, "")


def test_remove_returns_true_when_present(watch_dir):
    add_to_watchlist(watch_dir, "snap-004")
    assert remove_from_watchlist(watch_dir, "snap-004") is True


def test_remove_returns_false_when_absent(watch_dir):
    assert remove_from_watchlist(watch_dir, "snap-999") is False


def test_remove_actually_deletes(watch_dir):
    add_to_watchlist(watch_dir, "snap-005")
    remove_from_watchlist(watch_dir, "snap-005")
    assert not is_watched(watch_dir, "snap-005")


def test_is_watched_true(watch_dir):
    add_to_watchlist(watch_dir, "snap-006")
    assert is_watched(watch_dir, "snap-006") is True


def test_is_watched_false(watch_dir):
    assert is_watched(watch_dir, "snap-007") is False


def test_get_watchlist_empty(watch_dir):
    assert get_watchlist(watch_dir) == {}


def test_get_watchlist_multiple(watch_dir):
    add_to_watchlist(watch_dir, "snap-010")
    add_to_watchlist(watch_dir, "snap-011")
    data = get_watchlist(watch_dir)
    assert len(data) == 2


def test_clear_returns_count(watch_dir):
    add_to_watchlist(watch_dir, "snap-020")
    add_to_watchlist(watch_dir, "snap-021")
    assert clear_watchlist(watch_dir) == 2


def test_clear_empties_watchlist(watch_dir):
    add_to_watchlist(watch_dir, "snap-022")
    clear_watchlist(watch_dir)
    assert get_watchlist(watch_dir) == {}


def test_clear_empty_returns_zero(watch_dir):
    assert clear_watchlist(watch_dir) == 0
