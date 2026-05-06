"""Rename / relabel snapshots without losing their content."""

from __future__ import annotations

import json
from pathlib import Path


def _snap_path(snapshot_dir: Path, name: str) -> Path:
    return snapshot_dir / f"{name}.json"


def _load(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def _save(path: Path, data: dict) -> None:
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def rename_snapshot(
    snapshot_dir: Path,
    old_name: str,
    new_name: str,
    *,
    overwrite: bool = False,
) -> dict:
    """Rename *old_name* to *new_name* inside *snapshot_dir*.

    Returns a result dict with keys:
      - ``ok`` (bool)
      - ``reason`` (str | None) – human-readable error when ok is False
    """
    src = _snap_path(snapshot_dir, old_name)
    dst = _snap_path(snapshot_dir, new_name)

    if not src.exists():
        return {"ok": False, "reason": f"snapshot '{old_name}' not found"}

    if not new_name or not new_name.strip():
        return {"ok": False, "reason": "new name must not be empty"}

    if dst.exists() and not overwrite:
        return {"ok": False, "reason": f"snapshot '{new_name}' already exists (use overwrite=True to replace)"}

    data = _load(src)
    data["label"] = new_name
    _save(dst, data)
    src.unlink()
    return {"ok": True, "reason": None}


def relabel_snapshot(
    snapshot_dir: Path,
    name: str,
    new_label: str,
) -> dict:
    """Update only the *label* field inside an existing snapshot file.

    The file name on disk stays the same; only the embedded label changes.
    Returns a result dict with keys ``ok`` and ``reason``.
    """
    path = _snap_path(snapshot_dir, name)

    if not path.exists():
        return {"ok": False, "reason": f"snapshot '{name}' not found"}

    if not new_label or not new_label.strip():
        return {"ok": False, "reason": "new label must not be empty"}

    data = _load(path)
    old_label = data.get("label")
    data["label"] = new_label.strip()
    _save(path, data)
    return {"ok": True, "reason": None, "old_label": old_label}
