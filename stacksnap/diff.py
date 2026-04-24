"""Diff two snapshots and report what changed between them."""

from __future__ import annotations

from typing import Any


def _diff_section(key: str, old: Any, new: Any) -> dict:
    """Return a diff entry for a single snapshot section."""
    if old == new:
        return {"status": "unchanged", "old": old, "new": new}
    return {"status": "changed", "old": old, "new": new}


def diff_snapshots(snap_a: dict, snap_b: dict) -> dict:
    """Compare two snapshot dicts and return a structured diff.

    Args:
        snap_a: The baseline snapshot (older / left side).
        snap_b: The target snapshot (newer / right side).

    Returns:
        A dict keyed by section name, each containing a diff entry.
    """
    sections = {
        "python",
        "node",
        "env_vars",
        "git_branch",
        "git_commit",
    }

    result: dict[str, Any] = {
        "label_a": snap_a.get("label", "<unknown>"),
        "label_b": snap_b.get("label", "<unknown>"),
        "timestamp_a": snap_a.get("timestamp"),
        "timestamp_b": snap_b.get("timestamp"),
        "sections": {},
    }

    all_keys = sections | set(snap_a.keys()) | set(snap_b.keys())
    all_keys -= {"label", "timestamp"}  # handled above

    for key in sorted(all_keys):
        result["sections"][key] = _diff_section(
            key, snap_a.get(key), snap_b.get(key)
        )

    changed = [
        k for k, v in result["sections"].items() if v["status"] == "changed"
    ]
    result["has_changes"] = bool(changed)
    result["changed_keys"] = changed
    return result


def format_diff(diff: dict) -> str:
    """Render a diff dict as a human-readable string."""
    lines = [
        f"Diff: {diff['label_a']}  →  {diff['label_b']}",
        "-" * 50,
    ]
    if not diff["has_changes"]:
        lines.append("No changes detected.")
        return "\n".join(lines)

    for key in diff["changed_keys"]:
        entry = diff["sections"][key]
        lines.append(f"  {key}:")
        lines.append(f"    - {entry['old']}")
        lines.append(f"    + {entry['new']}")

    unchanged = [
        k
        for k, v in diff["sections"].items()
        if v["status"] == "unchanged"
    ]
    if unchanged:
        lines.append(f"  (unchanged: {', '.join(sorted(unchanged))})")

    return "\n".join(lines)
