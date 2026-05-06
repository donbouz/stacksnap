"""Bookmark management for stacksnap snapshots.

A bookmark is a named shortcut pointing to a snapshot ID, similar to an alias
but semantically intended for quick navigation rather than renaming.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_BOOKMARKS_FILE = "bookmarks.json"


def _bookmarks_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _BOOKMARKS_FILE


def _load_bookmarks(snapshot_dir: Path) -> Dict[str, str]:
    path = _bookmarks_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_bookmarks(snapshot_dir: Path, data: Dict[str, str]) -> None:
    _bookmarks_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_bookmark(snapshot_dir: Path, name: str, snapshot_id: str) -> bool:
    """Create or update a bookmark. Returns True if newly created."""
    if not name or not name.strip():
        raise ValueError("Bookmark name must not be empty.")
    if not snapshot_id or not snapshot_id.strip():
        raise ValueError("Snapshot ID must not be empty.")
    data = _load_bookmarks(snapshot_dir)
    is_new = name not in data
    data[name] = snapshot_id.strip()
    _save_bookmarks(snapshot_dir, data)
    return is_new


def remove_bookmark(snapshot_dir: Path, name: str) -> bool:
    """Remove a bookmark by name. Returns True if it existed."""
    data = _load_bookmarks(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_bookmarks(snapshot_dir, data)
    return True


def resolve_bookmark(snapshot_dir: Path, name: str) -> Optional[str]:
    """Return the snapshot ID for a bookmark name, or None if not found."""
    return _load_bookmarks(snapshot_dir).get(name)


def list_bookmarks(snapshot_dir: Path) -> List[Dict[str, str]]:
    """Return all bookmarks as a list of {name, snapshot_id} dicts."""
    data = _load_bookmarks(snapshot_dir)
    return [{"name": k, "snapshot_id": v} for k, v in sorted(data.items())]
