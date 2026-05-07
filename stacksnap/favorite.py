"""Manage favorite (starred) snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

_FAVORITES_FILE = "favorites.json"


def _favorites_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _FAVORITES_FILE


def _load_favorites(snapshot_dir: Path) -> List[str]:
    path = _favorites_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_favorites(snapshot_dir: Path, favorites: List[str]) -> None:
    _favorites_path(snapshot_dir).write_text(json.dumps(favorites, indent=2))


def add_favorite(snapshot_id: str, snapshot_dir: Path) -> bool:
    """Star a snapshot. Returns True if newly added, False if already starred."""
    if not snapshot_id:
        raise ValueError("snapshot_id must not be empty")
    favorites = _load_favorites(snapshot_dir)
    if snapshot_id in favorites:
        return False
    favorites.append(snapshot_id)
    _save_favorites(snapshot_dir, favorites)
    return True


def remove_favorite(snapshot_id: str, snapshot_dir: Path) -> bool:
    """Unstar a snapshot. Returns True if removed, False if not present."""
    favorites = _load_favorites(snapshot_dir)
    if snapshot_id not in favorites:
        return False
    favorites.remove(snapshot_id)
    _save_favorites(snapshot_dir, favorites)
    return True


def is_favorite(snapshot_id: str, snapshot_dir: Path) -> bool:
    """Return True if the snapshot is starred."""
    return snapshot_id in _load_favorites(snapshot_dir)


def get_favorites(snapshot_dir: Path) -> List[str]:
    """Return all starred snapshot IDs."""
    return list(_load_favorites(snapshot_dir))
