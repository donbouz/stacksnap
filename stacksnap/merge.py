"""Merge two snapshots into a combined snapshot, with conflict resolution."""

from __future__ import annotations

import copy
from typing import Any

SECTIONS = ["python", "node", "env_vars", "git", "tools"]


def _merge_section(
    base: dict[str, Any],
    override: dict[str, Any],
    strategy: str = "override",
) -> tuple[dict[str, Any], list[str]]:
    """Merge two flat dicts.  Returns merged dict and list of conflict keys."""
    merged = copy.deepcopy(base)
    conflicts: list[str] = []

    for key, val in override.items():
        if key in merged and merged[key] != val:
            conflicts.append(key)
            if strategy == "override":
                merged[key] = val
            # strategy == "keep" => leave base value unchanged
        else:
            merged[key] = val

    return merged, conflicts


def merge_snapshots(
    snap_a: dict[str, Any],
    snap_b: dict[str, Any],
    name: str = "merged",
    strategy: str = "override",
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Merge snap_b into snap_a.

    Parameters
    ----------
    snap_a:   base snapshot
    snap_b:   snapshot whose values take precedence (when strategy='override')
    name:     label for the resulting snapshot
    strategy: 'override' — snap_b wins on conflict
              'keep'     — snap_a wins on conflict

    Returns
    -------
    (merged_snapshot, conflicts)  where conflicts maps section -> [conflict_keys]
    """
    if strategy not in {"override", "keep"}:
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: dict[str, Any] = {"label": name}
    all_conflicts: dict[str, list[str]] = {}

    for section in SECTIONS:
        base_sec = snap_a.get(section) or {}
        over_sec = snap_b.get(section) or {}

        if not isinstance(base_sec, dict) or not isinstance(over_sec, dict):
            # Non-dict sections: simple scalar merge
            merged[section] = over_sec if strategy == "override" else base_sec
            if base_sec != over_sec:
                all_conflicts[section] = [section]
            continue

        sec_merged, conflicts = _merge_section(base_sec, over_sec, strategy)
        merged[section] = sec_merged
        if conflicts:
            all_conflicts[section] = conflicts

    return merged, all_conflicts


def format_merge_report(conflicts: dict[str, list[str]], strategy: str) -> str:
    """Return a human-readable summary of merge conflicts."""
    if not conflicts:
        return "Merge completed with no conflicts."

    lines = [f"Merge completed (strategy={strategy!r}). Conflicts resolved:"]
    for section, keys in conflicts.items():
        lines.append(f"  [{section}] {', '.join(keys)}")
    return "\n".join(lines)
