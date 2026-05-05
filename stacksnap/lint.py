"""Lint snapshots for common issues and best-practice violations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WARN_MISSING_ENV_VARS = "env_vars section is empty — no environment variables captured"
WARN_MISSING_PYTHON = "python section is missing or has no 'version' key"
WARN_MISSING_NODE = "node section is missing or has no 'version' key"
WARN_LABEL_GENERIC = "label looks auto-generated; consider giving the snapshot a meaningful name"
WARN_NO_PACKAGES = "python section has no 'packages' key — dependency info may be incomplete"
INFO_LARGE_ENV = "env_vars contains more than 50 entries — consider filtering sensitive keys"


def _check_label(snapshot: dict[str, Any]) -> list[str]:
    label = snapshot.get("label", "")
    if not label or (label.startswith("snapshot-") and label[9:].isdigit()):
        return [WARN_LABEL_GENERIC]
    return []


def _check_python(snapshot: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    py = snapshot.get("python")
    if not py or "version" not in py:
        issues.append(WARN_MISSING_PYTHON)
    elif "packages" not in py:
        issues.append(WARN_NO_PACKAGES)
    return issues


def _check_node(snapshot: dict[str, Any]) -> list[str]:
    node = snapshot.get("node")
    if not node or "version" not in node:
        return [WARN_MISSING_NODE]
    return []


def _check_env_vars(snapshot: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    env = snapshot.get("env_vars", {})
    if not env:
        issues.append(WARN_MISSING_ENV_VARS)
    elif len(env) > 50:
        issues.append(INFO_LARGE_ENV)
    return issues


def lint_snapshot(snapshot: dict[str, Any]) -> list[str]:
    """Return a list of lint messages for *snapshot*. Empty list means clean."""
    issues: list[str] = []
    issues.extend(_check_label(snapshot))
    issues.extend(_check_python(snapshot))
    issues.extend(_check_node(snapshot))
    issues.extend(_check_env_vars(snapshot))
    return issues


def lint_snapshot_file(path: Path) -> list[str]:
    """Load a snapshot JSON file and lint it."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return [f"cannot read snapshot file: {exc}"]
    return lint_snapshot(data)


def format_lint_report(snapshot_id: str, issues: list[str]) -> str:
    """Format lint results for display."""
    if not issues:
        return f"{snapshot_id}: OK"
    lines = [f"{snapshot_id}: {len(issues)} issue(s)"]
    for issue in issues:
        lines.append(f"  • {issue}")
    return "\n".join(lines)
