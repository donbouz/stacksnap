"""Watchlist: track snapshots of interest for quick access and monitoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

_WATCHLIST_FILE = "watchlist.json"


def _load_watchlist(directory: Path) -> Dict[str, List[str]]:
    path = directory / _WATCHLIST_FILE
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_watchlist(directory: Path, data: Dict[str, List[str]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / _WATCHLIST_FILE).open("w") as fh:
        json.dump(data, fh, indent=2)


def add_to_watchlist(directory: Path, snapshot_id: str, reason: str = "") -> bool:
    """Add a snapshot to the watchlist. Returns True if newly added."""
    if not snapshot_id:
        raise ValueError("snapshot_id must not be empty")
    data = _load_watchlist(directory)
    if snapshot_id in data:
        return False
    data[snapshot_id] = {"reason": reason.strip()}
    _save_watchlist(directory, data)
    return True


def remove_from_watchlist(directory: Path, snapshot_id: str) -> bool:
    """Remove a snapshot from the watchlist. Returns True if it was present."""
    data = _load_watchlist(directory)
    if snapshot_id not in data:
        return False
    del data[snapshot_id]
    _save_watchlist(directory, data)
    return True


def get_watchlist(directory: Path) -> Dict[str, dict]:
    """Return all watched snapshots with their metadata."""
    return _load_watchlist(directory)


def is_watched(directory: Path, snapshot_id: str) -> bool:
    """Return True if the snapshot is on the watchlist."""
    return snapshot_id in _load_watchlist(directory)


def clear_watchlist(directory: Path) -> int:
    """Remove all entries. Returns count of removed items."""
    data = _load_watchlist(directory)
    count = len(data)
    _save_watchlist(directory, {})
    return count
