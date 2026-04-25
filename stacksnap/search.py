"""Search snapshots by metadata fields, tags, and content."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stacksnap.snapshot import list_snapshots, load_snapshot
from stacksnap.tags import get_tags


def _matches_query(snapshot: dict[str, Any], query: str) -> bool:
    """Return True if *query* appears in any string value of the snapshot."""
    q = query.lower()
    for value in snapshot.values():
        if isinstance(value, str) and q in value.lower():
            return True
        if isinstance(value, dict):
            for v in value.values():
                if isinstance(v, str) and q in v.lower():
                    return True
    return False


def search_snapshots(
    snapshots_dir: Path,
    *,
    query: str | None = None,
    tag: str | None = None,
    python_version: str | None = None,
    node_version: str | None = None,
) -> list[dict[str, Any]]:
    """Return snapshots matching all supplied filters.

    Parameters
    ----------
    snapshots_dir:
        Directory that contains snapshot JSON files.
    query:
        Free-text substring matched against any string field.
    tag:
        Only include snapshots that carry this tag.
    python_version:
        Exact Python version string to match.
    node_version:
        Exact Node version string to match.
    """
    results: list[dict[str, Any]] = []

    for name in list_snapshots(snapshots_dir):
        snap = load_snapshot(name, snapshots_dir)
        if snap is None:
            continue

        if query and not _matches_query(snap, query):
            continue

        if tag:
            tags = get_tags(name, snapshots_dir)
            if tag not in tags:
                continue

        if python_version:
            recorded = snap.get("python", {}).get("version", "")
            if python_version not in recorded:
                continue

        if node_version:
            recorded = snap.get("node", {}).get("version", "")
            if node_version not in recorded:
                continue

        results.append(snap)

    return results


def format_search_results(results: list[dict[str, Any]]) -> str:
    """Return a human-readable summary of search results."""
    if not results:
        return "No snapshots matched."
    lines: list[str] = []
    for snap in results:
        label = snap.get("label", "<unknown>")
        ts = snap.get("timestamp", "")
        py = snap.get("python", {}).get("version", "n/a")
        node = snap.get("node", {}).get("version", "n/a")
        lines.append(f"  {label}  [{ts}]  python={py}  node={node}")
    return "\n".join(lines)
