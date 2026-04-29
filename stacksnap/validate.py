"""Validate snapshot integrity and schema conformance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_KEYS = {"label", "timestamp", "python", "node", "env"}
REQUIRED_PYTHON_KEYS = {"version", "packages"}
REQUIRED_NODE_KEYS = {"version", "packages"}


def _check_section(section: Any, required_keys: set[str], section_name: str) -> list[str]:
    """Return a list of validation errors for a single section dict."""
    errors: list[str] = []
    if not isinstance(section, dict):
        errors.append(f"'{section_name}' must be a mapping, got {type(section).__name__}")
        return errors
    for key in required_keys:
        if key not in section:
            errors.append(f"'{section_name}' is missing required key '{key}'")
    return errors


def validate_snapshot(snapshot: dict[str, Any]) -> list[str]:
    """Validate a snapshot dict and return a list of error strings.

    An empty list means the snapshot is valid.
    """
    errors: list[str] = []

    if not isinstance(snapshot, dict):
        return [f"Snapshot must be a mapping, got {type(snapshot).__name__}"]

    for key in REQUIRED_TOP_KEYS:
        if key not in snapshot:
            errors.append(f"Snapshot is missing required top-level key '{key}'")

    if "python" in snapshot:
        errors.extend(_check_section(snapshot["python"], REQUIRED_PYTHON_KEYS, "python"))

    if "node" in snapshot:
        errors.extend(_check_section(snapshot["node"], REQUIRED_NODE_KEYS, "node"))

    if "env" in snapshot and not isinstance(snapshot["env"], dict):
        errors.append(f"'env' must be a mapping, got {type(snapshot['env']).__name__}")

    return errors


def validate_snapshot_file(path: Path) -> list[str]:
    """Load a snapshot JSON file and validate it, returning error strings."""
    if not path.exists():
        return [f"File not found: {path}"]
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in {path}: {exc}"]
    return validate_snapshot(data)


def is_valid(snapshot: dict[str, Any]) -> bool:
    """Return True if the snapshot passes all validation checks."""
    return len(validate_snapshot(snapshot)) == 0
