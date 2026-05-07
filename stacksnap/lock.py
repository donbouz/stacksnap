"""Snapshot locking — prevent accidental modification of important snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_LOCKS_FILE = "locks.json"


def _locks_path(directory: str) -> Path:
    return Path(directory) / _LOCKS_FILE


def _load_locks(directory: str) -> List[str]:
    p = _locks_path(directory)
    if not p.exists():
        return []
    with p.open() as fh:
        return json.load(fh)


def _save_locks(directory: str, locks: List[str]) -> None:
    p = _locks_path(directory)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as fh:
        json.dump(locks, fh, indent=2)


def lock_snapshot(snapshot_id: str, directory: str) -> bool:
    """Lock a snapshot. Returns True if newly locked, False if already locked."""
    if not snapshot_id:
        raise ValueError("snapshot_id must not be empty")
    locks = _load_locks(directory)
    if snapshot_id in locks:
        return False
    locks.append(snapshot_id)
    _save_locks(directory, locks)
    return True


def unlock_snapshot(snapshot_id: str, directory: str) -> bool:
    """Unlock a snapshot. Returns True if removed, False if was not locked."""
    locks = _load_locks(directory)
    if snapshot_id not in locks:
        return False
    locks.remove(snapshot_id)
    _save_locks(directory, locks)
    return True


def is_locked(snapshot_id: str, directory: str) -> bool:
    """Return True if the snapshot is currently locked."""
    return snapshot_id in _load_locks(directory)


def get_locked(directory: str) -> List[str]:
    """Return all locked snapshot IDs."""
    return list(_load_locks(directory))


def clear_locks(directory: str) -> int:
    """Remove all locks. Returns count of locks cleared."""
    locks = _load_locks(directory)
    count = len(locks)
    _save_locks(directory, [])
    return count
