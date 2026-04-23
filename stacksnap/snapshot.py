"""Core snapshot module for capturing and restoring dev environment state."""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

SNAPSHOT_DIR = Path.home() / ".stacksnap" / "snapshots"


def _run(cmd: list[str]) -> str:
    """Run a shell command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def capture_snapshot(name: Optional[str] = None) -> dict:
    """Capture the current dev environment state and return a snapshot dict."""
    timestamp = datetime.utcnow().isoformat()
    label = name or f"snap-{timestamp}"

    snapshot = {
        "label": label,
        "timestamp": timestamp,
        "cwd": str(Path.cwd()),
        "python_version": _run(["python", "--version"]),
        "node_version": _run(["node", "--version"]),
        "git_branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "git_commit": _run(["git", "rev-parse", "HEAD"]),
        "pip_packages": _run(["pip", "freeze"]),
        "env_vars": {
            k: v
            for k, v in os.environ.items()
            if k.startswith(("PROJECT_", "APP_", "DATABASE_", "REDIS_", "API_"))
        },
    }
    return snapshot


def save_snapshot(snapshot: dict) -> Path:
    """Persist a snapshot to disk and return the file path."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe_label = snapshot["label"].replace(" ", "_").replace("/", "-")
    path = SNAPSHOT_DIR / f"{safe_label}.json"
    path.write_text(json.dumps(snapshot, indent=2))
    return path


def load_snapshot(label: str) -> dict:
    """Load a snapshot by label. Raises FileNotFoundError if not found."""
    safe_label = label.replace(" ", "_").replace("/", "-")
    path = SNAPSHOT_DIR / f"{safe_label}.json"
    if not path.exists():
        raise FileNotFoundError(f"No snapshot found with label: {label!r}")
    return json.loads(path.read_text())


def list_snapshots() -> list[dict]:
    """Return metadata for all saved snapshots, sorted newest first."""
    if not SNAPSHOT_DIR.exists():
        return []
    snapshots = []
    for p in SNAPSHOT_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            snapshots.append({"label": data["label"], "timestamp": data["timestamp"], "cwd": data["cwd"]})
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(snapshots, key=lambda s: s["timestamp"], reverse=True)


def delete_snapshot(label: str) -> bool:
    """Delete a snapshot by label. Returns True if deleted, False if not found."""
    safe_label = label.replace(" ", "_").replace("/", "-")
    path = SNAPSHOT_DIR / f"{safe_label}.json"
    if path.exists():
        path.unlink()
        return True
    return False
