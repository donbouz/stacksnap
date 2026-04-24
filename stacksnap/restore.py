"""Restore a previously captured dev environment snapshot."""

import subprocess
import sys
from typing import Optional

from stacksnap.snapshot import load_snapshot


def _run_silent(cmd: list[str]) -> tuple[int, str]:
    """Run a shell command and return (returncode, combined output)."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.returncode, result.stdout.strip()


def restore_python(snapshot: dict) -> list[str]:
    """Reinstall Python packages from snapshot. Returns list of warnings."""
    warnings = []
    packages = snapshot.get("python_packages", [])
    if not packages:
        return warnings

    for pkg in packages:
        code, out = _run_silent([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        if code != 0:
            warnings.append(f"pip: failed to install '{pkg}': {out}")
    return warnings


def restore_node(snapshot: dict) -> list[str]:
    """Reinstall Node packages from snapshot. Returns list of warnings."""
    warnings = []
    packages = snapshot.get("node_packages", [])
    if not packages:
        return warnings

    for pkg in packages:
        code, out = _run_silent(["npm", "install", "-g", pkg, "--quiet"])
        if code != 0:
            warnings.append(f"npm: failed to install '{pkg}': {out}")
    return warnings


def restore_env_vars(snapshot: dict) -> dict[str, str]:
    """Return env vars captured in the snapshot (caller must apply them)."""
    return snapshot.get("env_vars", {})


def restore_snapshot(
    label: str,
    snapshots_dir: Optional[str] = None,
    *,
    restore_python_pkgs: bool = True,
    restore_node_pkgs: bool = True,
) -> dict:
    """
    Load a snapshot by label and attempt to restore the environment.

    Returns a result dict with keys:
      - 'label': the snapshot label
      - 'warnings': list of non-fatal issues encountered
      - 'env_vars': dict of env vars from the snapshot
    """
    snapshot = load_snapshot(label, snapshots_dir=snapshots_dir)
    warnings: list[str] = []

    if restore_python_pkgs:
        warnings.extend(restore_python(snapshot))

    if restore_node_pkgs:
        warnings.extend(restore_node(snapshot))

    env_vars = restore_env_vars(snapshot)

    return {
        "label": label,
        "warnings": warnings,
        "env_vars": env_vars,
    }
