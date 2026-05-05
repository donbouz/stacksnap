"""Audit log for snapshot operations (capture, restore, archive, etc.)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUDIT_FILE = os.path.expanduser("~/.stacksnap/audit.jsonl")


def _audit_path(audit_file: str | None = None) -> Path:
    return Path(audit_file or DEFAULT_AUDIT_FILE)


def record_event(
    action: str,
    snapshot_id: str,
    details: dict[str, Any] | None = None,
    audit_file: str | None = None,
) -> dict[str, Any]:
    """Append a single audit event and return the entry."""
    if not action or not action.strip():
        raise ValueError("action must be a non-empty string")
    if not snapshot_id or not snapshot_id.strip():
        raise ValueError("snapshot_id must be a non-empty string")

    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action.strip(),
        "snapshot_id": snapshot_id.strip(),
        "details": details or {},
    }

    path = _audit_path(audit_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    return entry


def get_events(
    snapshot_id: str | None = None,
    action: str | None = None,
    audit_file: str | None = None,
) -> list[dict[str, Any]]:
    """Return audit events, optionally filtered by snapshot_id and/or action."""
    path = _audit_path(audit_file)
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if snapshot_id and entry.get("snapshot_id") != snapshot_id:
                continue
            if action and entry.get("action") != action:
                continue
            events.append(entry)

    return events


def clear_events(audit_file: str | None = None) -> int:
    """Delete all audit events and return the count that were removed."""
    path = _audit_path(audit_file)
    if not path.exists():
        return 0
    events = get_events(audit_file=audit_file)
    path.unlink()
    return len(events)
