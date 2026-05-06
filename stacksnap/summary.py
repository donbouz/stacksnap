"""Generate a human-readable summary report for a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_snapshot(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def summarise_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Extract key headline fields from a snapshot dict."""
    python = snapshot.get("python", {})
    node = snapshot.get("node", {})
    env_vars = snapshot.get("env_vars", {})
    git = snapshot.get("git", {})

    return {
        "label": snapshot.get("label", "<unlabelled>"),
        "captured_at": snapshot.get("captured_at", "unknown"),
        "python_version": python.get("version", "n/a"),
        "virtualenv": python.get("virtualenv") or "none",
        "node_version": node.get("version", "n/a"),
        "env_var_count": len(env_vars),
        "git_branch": git.get("branch", "n/a"),
        "git_commit": git.get("commit", "n/a"),
    }


def format_summary(summary: dict[str, Any]) -> str:
    """Render a summary dict as a readable multi-line string."""
    lines = [
        f"Snapshot : {summary['label']}",
        f"Captured : {summary['captured_at']}",
        "-" * 40,
        f"Python   : {summary['python_version']}",
        f"Virtualenv: {summary['virtualenv']}",
        f"Node     : {summary['node_version']}",
        f"Env vars : {summary['env_var_count']} variable(s)",
        f"Git branch: {summary['git_branch']}",
        f"Git commit: {summary['git_commit']}",
    ]
    return "\n".join(lines)


def summarise_snapshot_file(snapshot_path: Path) -> str:
    """Load a snapshot file and return its formatted summary."""
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")
    snapshot = _load_snapshot(snapshot_path)
    summary = summarise_snapshot(snapshot)
    return format_summary(summary)
