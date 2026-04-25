"""Pin snapshots to prevent accidental deletion or overwrite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_PINS_FILE = "pins.json"


def _load_pins(snapshot_dir: Path) -> List[str]:
    """Return list of pinned snapshot labels."""
    pins_path = snapshot_dir / _PINS_FILE
    if not pins_path.exists():
        return []
    with pins_path.open() as fh:
        return json.load(fh)


def _save_pins(snapshot_dir: Path, pins: List[str]) -> None:
    pins_path = snapshot_dir / _PINS_FILE
    with pins_path.open("w") as fh:
        json.dump(pins, fh, indent=2)


def pin_snapshot(snapshot_dir: Path, label: str) -> bool:
    """Pin *label*. Returns True if newly pinned, False if already pinned."""
    pins = _load_pins(snapshot_dir)
    if label in pins:
        return False
    pins.append(label)
    _save_pins(snapshot_dir, pins)
    return True


def unpin_snapshot(snapshot_dir: Path, label: str) -> bool:
    """Unpin *label*. Returns True if removed, False if not found."""
    pins = _load_pins(snapshot_dir)
    if label not in pins:
        return False
    pins.remove(label)
    _save_pins(snapshot_dir, pins)
    return True


def is_pinned(snapshot_dir: Path, label: str) -> bool:
    """Return True if *label* is currently pinned."""
    return label in _load_pins(snapshot_dir)


def list_pinned(snapshot_dir: Path) -> List[str]:
    """Return all pinned snapshot labels."""
    return list(_load_pins(snapshot_dir))
