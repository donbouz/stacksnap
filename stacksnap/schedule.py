"""Scheduled automatic snapshot support for stacksnap."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_SCHEDULE_FILE = Path.home() / ".stacksnap" / "schedules.json"


def _load_schedules(schedule_file: Path = DEFAULT_SCHEDULE_FILE) -> dict:
    if schedule_file.exists():
        with open(schedule_file) as f:
            return json.load(f)
    return {}


def _save_schedules(data: dict, schedule_file: Path = DEFAULT_SCHEDULE_FILE) -> None:
    schedule_file.parent.mkdir(parents=True, exist_ok=True)
    with open(schedule_file, "w") as f:
        json.dump(data, f, indent=2)


def add_schedule(
    project: str,
    interval_minutes: int,
    label_prefix: str = "auto",
    schedule_file: Path = DEFAULT_SCHEDULE_FILE,
) -> dict:
    """Register a scheduled snapshot for a project."""
    if interval_minutes < 1:
        raise ValueError("interval_minutes must be >= 1")
    data = _load_schedules(schedule_file)
    entry = {
        "project": project,
        "interval_minutes": interval_minutes,
        "label_prefix": label_prefix,
        "last_run": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    data[project] = entry
    _save_schedules(data, schedule_file)
    return entry


def remove_schedule(
    project: str, schedule_file: Path = DEFAULT_SCHEDULE_FILE
) -> bool:
    """Remove a scheduled snapshot entry. Returns True if removed."""
    data = _load_schedules(schedule_file)
    if project not in data:
        return False
    del data[project]
    _save_schedules(data, schedule_file)
    return True


def get_schedule(
    project: str, schedule_file: Path = DEFAULT_SCHEDULE_FILE
) -> Optional[dict]:
    """Retrieve schedule entry for a project, or None."""
    return _load_schedules(schedule_file).get(project)


def list_schedules(schedule_file: Path = DEFAULT_SCHEDULE_FILE) -> list:
    """Return all scheduled entries as a list."""
    return list(_load_schedules(schedule_file).values())


def is_due(project: str, schedule_file: Path = DEFAULT_SCHEDULE_FILE) -> bool:
    """Return True if the project's snapshot is due to run."""
    entry = get_schedule(project, schedule_file)
    if entry is None:
        return False
    if entry["last_run"] is None:
        return True
    last = datetime.fromisoformat(entry["last_run"])
    elapsed = (datetime.utcnow() - last).total_seconds() / 60
    return elapsed >= entry["interval_minutes"]


def mark_ran(
    project: str, schedule_file: Path = DEFAULT_SCHEDULE_FILE
) -> None:
    """Update last_run timestamp for a project schedule."""
    data = _load_schedules(schedule_file)
    if project in data:
        data[project]["last_run"] = datetime.utcnow().isoformat()
        _save_schedules(data, schedule_file)
