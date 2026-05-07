"""Tests for stacksnap.favorite."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from stacksnap.favorite import (
    add_favorite,
    remove_favorite,
    is_favorite,
    get_favorites,
)


@pytest.fixture()
def fav_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_favorite_returns_true_when_new(fav_dir: Path) -> None:
    assert add_favorite("snap-001", fav_dir) is True


def test_add_favorite_returns_false_when_duplicate(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    assert add_favorite("snap-001", fav_dir) is False


def test_add_favorite_persists(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    data = json.loads((fav_dir / "favorites.json").read_text())
    assert "snap-001" in data


def test_add_multiple_favorites(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    add_favorite("snap-002", fav_dir)
    favs = get_favorites(fav_dir)
    assert "snap-001" in favs
    assert "snap-002" in favs


def test_add_favorite_empty_id_raises(fav_dir: Path) -> None:
    with pytest.raises(ValueError):
        add_favorite("", fav_dir)


def test_remove_favorite_returns_true_when_present(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    assert remove_favorite("snap-001", fav_dir) is True


def test_remove_favorite_returns_false_when_absent(fav_dir: Path) -> None:
    assert remove_favorite("snap-999", fav_dir) is False


def test_remove_favorite_actually_removes(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    remove_favorite("snap-001", fav_dir)
    assert is_favorite("snap-001", fav_dir) is False


def test_is_favorite_returns_true_when_starred(fav_dir: Path) -> None:
    add_favorite("snap-001", fav_dir)
    assert is_favorite("snap-001", fav_dir) is True


def test_is_favorite_returns_false_when_not_starred(fav_dir: Path) -> None:
    assert is_favorite("snap-001", fav_dir) is False


def test_get_favorites_empty_when_no_file(fav_dir: Path) -> None:
    assert get_favorites(fav_dir) == []


def test_get_favorites_returns_all(fav_dir: Path) -> None:
    add_favorite("snap-A", fav_dir)
    add_favorite("snap-B", fav_dir)
    assert set(get_favorites(fav_dir)) == {"snap-A", "snap-B"}
