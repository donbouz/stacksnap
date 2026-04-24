"""Lifecycle hooks: run shell commands before/after tag-triggered operations."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

HOOKS_FILE = "hooks.json"


def _load_hooks(snapshot_dir: Path) -> Dict[str, List[str]]:
    hooks_path = snapshot_dir / HOOKS_FILE
    if hooks_path.exists():
        return json.loads(hooks_path.read_text())
    return {}


def _save_hooks(snapshot_dir: Path, hooks: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / HOOKS_FILE).write_text(json.dumps(hooks, indent=2))


def register_hook(snapshot_dir: Path, event: str, command: str) -> None:
    """Register a shell command for a lifecycle event (e.g. 'pre-restore')."""
    hooks = _load_hooks(snapshot_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(snapshot_dir, hooks)


def unregister_hook(snapshot_dir: Path, event: str, command: str) -> bool:
    """Remove a command from an event. Returns True if it was present."""
    hooks = _load_hooks(snapshot_dir)
    cmds = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    hooks[event] = cmds
    _save_hooks(snapshot_dir, hooks)
    return True


def get_hooks(snapshot_dir: Path, event: str) -> List[str]:
    """Return all registered commands for an event."""
    return _load_hooks(snapshot_dir).get(event, [])


def run_hooks(
    snapshot_dir: Path,
    event: str,
    env: Optional[dict] = None,
) -> List[dict]:
    """Execute all hooks for an event. Returns list of result dicts."""
    results = []
    for cmd in get_hooks(snapshot_dir, event):
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env,
            )
            results.append(
                {
                    "command": cmd,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout.strip(),
                    "stderr": proc.stderr.strip(),
                    "success": proc.returncode == 0,
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {"command": cmd, "returncode": -1, "error": str(exc), "success": False}
            )
    return results


def list_all_hooks(snapshot_dir: Path) -> Dict[str, List[str]]:
    """Return the full hooks registry."""
    return _load_hooks(snapshot_dir)
