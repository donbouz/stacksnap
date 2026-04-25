"""Batch runner: iterate all schedules and fire snapshots that are due."""

from __future__ import annotations

import logging
from typing import List

from stacksnap.schedule import list_schedules, is_due, mark_ran
from stacksnap.snapshot import capture_snapshot, save_snapshot

logger = logging.getLogger(__name__)


def run_due_snapshots(dry_run: bool = False) -> List[dict]:
    """Check all schedules and capture snapshots for those that are due.

    Returns a list of result dicts with keys: project, status, path/error.
    """
    results = []
    for entry in list_schedules():
        project = entry["project"]
        if not is_due(project):
            logger.debug("'%s' is not due — skipping.", project)
            continue
        label = f"{entry['label_prefix']}-{project}"
        if dry_run:
            logger.info("[dry-run] Would snapshot '%s' as '%s'.", project, label)
            results.append({"project": project, "status": "dry-run", "path": None})
            continue
        try:
            snap = capture_snapshot(name=label)
            path = save_snapshot(snap)
            mark_ran(project)
            logger.info("Snapshot saved for '%s': %s", project, path)
            results.append({"project": project, "status": "ok", "path": path})
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to snapshot '%s': %s", project, exc)
            results.append({"project": project, "status": "error", "error": str(exc)})
    return results


def summarise(results: List[dict]) -> str:
    """Return a human-readable summary of run_due_snapshots results."""
    if not results:
        return "No snapshots were due."
    lines = []
    for r in results:
        if r["status"] == "ok":
            lines.append(f"  ✓ {r['project']} → {r['path']}")
        elif r["status"] == "dry-run":
            lines.append(f"  ~ {r['project']} (dry-run)")
        else:
            lines.append(f"  ✗ {r['project']}: {r.get('error', 'unknown error')}")
    return "\n".join(lines)
