"""Tests for stacksnap.bookmark."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)


@pytest.fixture()
def bm_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_bookmark_returns_true_when_new(bm_dir: Path) -> None:
    assert set_bookmark(bm_dir, "mybm", "snap-001") is True


def test_set_bookmark_returns_false_when_overwrite(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "mybm", "snap-001")
    assert set_bookmark(bm_dir, "mybm", "snap-002") is False


def test_set_bookmark_persists(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "alpha", "snap-abc")
    raw = json.loads((bm_dir / "bookmarks.json").read_text())
    assert raw["alpha"] == "snap-abc"


def test_set_bookmark_overwrites_value(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "alpha", "snap-old")
    set_bookmark(bm_dir, "alpha", "snap-new")
    assert resolve_bookmark(bm_dir, "alpha") == "snap-new"


def test_set_bookmark_strips_snapshot_id(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "trimmed", "  snap-xyz  ")
    assert resolve_bookmark(bm_dir, "trimmed") == "snap-xyz"


def test_set_bookmark_empty_name_raises(bm_dir: Path) -> None:
    with pytest.raises(ValueError):
        set_bookmark(bm_dir, "", "snap-001")


def test_set_bookmark_empty_id_raises(bm_dir: Path) -> None:
    with pytest.raises(ValueError):
        set_bookmark(bm_dir, "bm", "")


def test_remove_bookmark_returns_true_when_present(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "bm", "snap-001")
    assert remove_bookmark(bm_dir, "bm") is True


def test_remove_bookmark_returns_false_when_absent(bm_dir: Path) -> None:
    assert remove_bookmark(bm_dir, "nonexistent") is False


def test_remove_bookmark_deletes_entry(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "bm", "snap-001")
    remove_bookmark(bm_dir, "bm")
    assert resolve_bookmark(bm_dir, "bm") is None


def test_resolve_returns_none_when_missing(bm_dir: Path) -> None:
    assert resolve_bookmark(bm_dir, "ghost") is None


def test_list_bookmarks_empty(bm_dir: Path) -> None:
    assert list_bookmarks(bm_dir) == []


def test_list_bookmarks_sorted(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "z-bm", "snap-z")
    set_bookmark(bm_dir, "a-bm", "snap-a")
    names = [b["name"] for b in list_bookmarks(bm_dir)]
    assert names == ["a-bm", "z-bm"]


def test_list_bookmarks_contains_snapshot_id(bm_dir: Path) -> None:
    set_bookmark(bm_dir, "check", "snap-check")
    bms = list_bookmarks(bm_dir)
    assert bms[0]["snapshot_id"] == "snap-check"
