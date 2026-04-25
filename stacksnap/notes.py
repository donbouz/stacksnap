"""Attach and retrieve freeform notes on snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

_NOTES_FILE = "notes.json"


def _load_notes(snapshot_dir: Path) -> dict:
    path = snapshot_dir / _NOTES_FILE
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_notes(snapshot_dir: Path, data: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / _NOTES_FILE).write_text(json.dumps(data, indent=2))


def add_note(snapshot_id: str, text: str, snapshot_dir: Path) -> dict:
    """Append a timestamped note to *snapshot_id*. Returns the new note entry."""
    if not text or not text.strip():
        raise ValueError("Note text must not be empty.")
    notes = _load_notes(snapshot_dir)
    entry = {
        "text": text.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    notes.setdefault(snapshot_id, []).append(entry)
    _save_notes(snapshot_dir, notes)
    return entry


def get_notes(snapshot_id: str, snapshot_dir: Path) -> list:
    """Return all notes for *snapshot_id*, newest last."""
    return _load_notes(snapshot_dir).get(snapshot_id, [])


def delete_notes(snapshot_id: str, snapshot_dir: Path) -> bool:
    """Remove all notes for *snapshot_id*. Returns True if anything was deleted."""
    notes = _load_notes(snapshot_dir)
    if snapshot_id not in notes:
        return False
    del notes[snapshot_id]
    _save_notes(snapshot_dir, notes)
    return True


def format_notes(snapshot_id: str, entries: list) -> str:
    """Human-readable rendering of notes for a snapshot."""
    if not entries:
        return f"No notes for snapshot '{snapshot_id}'."
    lines = [f"Notes for '{snapshot_id}':"]
    for i, e in enumerate(entries, 1):
        lines.append(f"  [{i}] {e['timestamp']}  {e['text']}")
    return "\n".join(lines)
