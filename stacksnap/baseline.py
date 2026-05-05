"""Baseline management: mark a snapshot as the project baseline and compare against it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_BASELINE_FILE = "baseline.json"


def _baseline_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _BASELINE_FILE


def set_baseline(snapshot_id: str, snapshot_dir: Path) -> bool:
    """Pin *snapshot_id* as the baseline. Returns True if changed, False if already set."""
    path = _baseline_path(snapshot_dir)
    current = get_baseline(snapshot_dir)
    if current == snapshot_id:
        return False
    path.write_text(json.dumps({"baseline": snapshot_id}), encoding="utf-8")
    return True


def get_baseline(snapshot_dir: Path) -> Optional[str]:
    """Return the current baseline snapshot id, or None if unset."""
    path = _baseline_path(snapshot_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("baseline")
    except (json.JSONDecodeError, OSError):
        return None


def clear_baseline(snapshot_dir: Path) -> bool:
    """Remove the baseline marker. Returns True if it existed."""
    path = _baseline_path(snapshot_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def load_snapshot(snapshot_id: str, snapshot_dir: Path) -> dict:
    """Load a snapshot dict by id (filename stem)."""
    snap_file = snapshot_dir / f"{snapshot_id}.json"
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
    return json.loads(snap_file.read_text(encoding="utf-8"))


def diff_against_baseline(snapshot_id: str, snapshot_dir: Path) -> dict:
    """Return a simple diff dict between the baseline and *snapshot_id*."""
    baseline_id = get_baseline(snapshot_dir)
    if baseline_id is None:
        raise ValueError("No baseline is set.")
    base = load_snapshot(baseline_id, snapshot_dir)
    target = load_snapshot(snapshot_id, snapshot_dir)

    result: dict = {"baseline": baseline_id, "target": snapshot_id, "sections": {}}
    all_keys = set(base.keys()) | set(target.keys())
    for key in sorted(all_keys):
        b_val = base.get(key)
        t_val = target.get(key)
        if b_val != t_val:
            result["sections"][key] = {"baseline": b_val, "target": t_val}
    return result
