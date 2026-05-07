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


def _walk_files(root: Path) -> tuple[dict[str, str], list[str]]:
    """Walk root recursively. Returns (files_dict, skipped_paths) where skipped paths are unreadable."""
    files: dict[str, str] = {}
    skipped: list[str] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        try:
            files[rel] = p.read_text(errors="replace")
        except PermissionError:
            skipped.append(rel)
    return files, skipped


def capture_snapshot(name: Optional[str] = None) -> dict:
    """Capture the current dev environment state and return a snapshot dict."""
    timestamp = datetime.utcnow().isoformat()
    label = name or f"snap-{timestamp}"

    files, skipped = _walk_files(Path.cwd())
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
        "files": files,
        "skipped_files": skipped,
    }
    return snapshot


def save_snapshot(snapshot: dict, snap_dir: Optional[Path] = None) -> Path:
    """Persist a snapshot to disk and return the file path."""
    directory = Path(snap_dir) if snap_dir is not None else SNAPSHOT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    safe_label = snapshot["label"].replace(" ", "_").replace("/", "-")
    path = directory / f"{safe_label}.json"
    path.write_text(json.dumps(snapshot, indent=2))
    return path


def load_snapshot(label: str, snap_dir: Optional[Path] = None) -> dict:
    """Load a snapshot by label. Raises FileNotFoundError if not found."""
    directory = Path(snap_dir) if snap_dir is not None else SNAPSHOT_DIR
    safe_label = label.replace(" ", "_").replace("/", "-")
    path = directory / f"{safe_label}.json"
    if not path.exists():
        raise FileNotFoundError(f"No snapshot found with label: {label!r}")
    return json.loads(path.read_text())


def list_snapshots(snap_dir: Optional[Path] = None) -> list[dict]:
    """Return metadata for all saved snapshots, sorted newest first."""
    directory = Path(snap_dir) if snap_dir is not None else SNAPSHOT_DIR
    if not directory.exists():
        return []
    snapshots = []
    for p in directory.glob("*.json"):
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
