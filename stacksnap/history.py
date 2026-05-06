"""Track and query snapshot access/usage history."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

_HISTORY_FILE = "history.json"


def _history_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _HISTORY_FILE


def _load_history(snapshot_dir: Path) -> list[dict[str, Any]]:
    p = _history_path(snapshot_dir)
    if not p.exists():
        return []
    with p.open() as fh:
        return json.load(fh)


def _save_history(snapshot_dir: Path, entries: list[dict[str, Any]]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with _history_path(snapshot_dir).open("w") as fh:
        json.dump(entries, fh, indent=2)


def record_access(snapshot_dir: Path, snapshot_id: str, action: str = "view") -> dict[str, Any]:
    """Append an access entry for *snapshot_id* and return it."""
    if not snapshot_id:
        raise ValueError("snapshot_id must not be empty")
    entries = _load_history(snapshot_dir)
    entry: dict[str, Any] = {
        "snapshot_id": snapshot_id,
        "action": action,
        "timestamp": time.time(),
    }
    entries.append(entry)
    _save_history(snapshot_dir, entries)
    return entry


def get_history(
    snapshot_dir: Path,
    snapshot_id: str | None = None,
    action: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Return history entries, optionally filtered by snapshot_id and/or action."""
    entries = _load_history(snapshot_dir)
    if snapshot_id is not None:
        entries = [e for e in entries if e.get("snapshot_id") == snapshot_id]
    if action is not None:
        entries = [e for e in entries if e.get("action") == action]
    if limit is not None:
        entries = entries[-limit:]
    return entries


def clear_history(snapshot_dir: Path, snapshot_id: str | None = None) -> int:
    """Remove history entries. If *snapshot_id* given, remove only its entries.

    Returns the number of entries removed.
    """
    entries = _load_history(snapshot_dir)
    if snapshot_id is None:
        removed = len(entries)
        _save_history(snapshot_dir, [])
        return removed
    kept = [e for e in entries if e.get("snapshot_id") != snapshot_id]
    removed = len(entries) - len(kept)
    _save_history(snapshot_dir, kept)
    return removed


def most_accessed(snapshot_dir: Path, top_n: int = 5) -> list[tuple[str, int]]:
    """Return the *top_n* snapshot IDs ordered by access count (descending)."""
    entries = _load_history(snapshot_dir)
    counts: dict[str, int] = {}
    for e in entries:
        sid = e.get("snapshot_id", "")
        counts[sid] = counts.get(sid, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:top_n]
