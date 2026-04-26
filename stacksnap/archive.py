"""Archive and prune old snapshots based on retention policy."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_SNAPSHOT_DIR = Path.home() / ".stacksnap" / "snapshots"


def _load_snapshot(path: Path) -> Dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def get_snapshot_age_days(snapshot: Dict[str, Any]) -> float:
    """Return how many days old a snapshot is based on its timestamp."""
    ts = snapshot.get("timestamp")
    if not ts:
        return float("inf")
    created = datetime.fromisoformat(ts)
    return (datetime.utcnow() - created).total_seconds() / 86400


def list_archivable(
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    max_age_days: int = 30,
    keep_pinned: bool = True,
) -> List[Path]:
    """Return snapshot paths older than *max_age_days*."""
    from stacksnap.pin import is_pinned  # local import to avoid circular deps

    archivable = []
    for snap_file in sorted(snapshot_dir.glob("*.json")):
        try:
            snap = _load_snapshot(snap_file)
        except (json.JSONDecodeError, OSError):
            continue
        if keep_pinned and is_pinned(snap.get("name", ""), snapshot_dir.parent):
            continue
        if get_snapshot_age_days(snap) > max_age_days:
            archivable.append(snap_file)
    return archivable


def archive_snapshots(
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    archive_dir: Path | None = None,
    max_age_days: int = 30,
    keep_pinned: bool = True,
) -> List[str]:
    """Move old snapshots to *archive_dir*. Returns list of archived names."""
    if archive_dir is None:
        archive_dir = snapshot_dir.parent / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    targets = list_archivable(snapshot_dir, max_age_days, keep_pinned)
    archived = []
    for snap_file in targets:
        dest = archive_dir / snap_file.name
        shutil.move(str(snap_file), dest)
        archived.append(snap_file.stem)
    return archived


def purge_archive(
    archive_dir: Path | None = None,
    older_than_days: int = 90,
) -> List[str]:
    """Permanently delete archived snapshots older than *older_than_days*."""
    if archive_dir is None:
        archive_dir = Path.home() / ".stacksnap" / "archive"
    if not archive_dir.exists():
        return []

    purged = []
    for snap_file in archive_dir.glob("*.json"):
        try:
            snap = _load_snapshot(snap_file)
        except (json.JSONDecodeError, OSError):
            continue
        if get_snapshot_age_days(snap) > older_than_days:
            snap_file.unlink()
            purged.append(snap_file.stem)
    return purged
