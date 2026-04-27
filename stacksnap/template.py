"""Snapshot templates: save a snapshot as a reusable template and instantiate new snapshots from one."""

from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import Any

_DEFAULT_TEMPLATE_DIR = Path.home() / ".stacksnap" / "templates"


def _template_path(name: str, template_dir: Path) -> Path:
    return template_dir / f"{name}.json"


def save_template(name: str, snapshot: dict[str, Any], template_dir: Path = _DEFAULT_TEMPLATE_DIR) -> bool:
    """Persist *snapshot* as a named template.  Returns True if newly created, False if overwritten."""
    if not name or not name.strip():
        raise ValueError("Template name must not be empty.")
    template_dir.mkdir(parents=True, exist_ok=True)
    path = _template_path(name.strip(), template_dir)
    is_new = not path.exists()
    payload = copy.deepcopy(snapshot)
    payload["_template_name"] = name.strip()
    path.write_text(json.dumps(payload, indent=2))
    return is_new


def load_template(name: str, template_dir: Path = _DEFAULT_TEMPLATE_DIR) -> dict[str, Any]:
    """Load a template by name.  Raises FileNotFoundError if absent."""
    path = _template_path(name.strip(), template_dir)
    if not path.exists():
        raise FileNotFoundError(f"Template '{name}' not found.")
    return json.loads(path.read_text())


def list_templates(template_dir: Path = _DEFAULT_TEMPLATE_DIR) -> list[str]:
    """Return sorted list of available template names."""
    if not template_dir.exists():
        return []
    return sorted(p.stem for p in template_dir.glob("*.json"))


def delete_template(name: str, template_dir: Path = _DEFAULT_TEMPLATE_DIR) -> bool:
    """Delete a template.  Returns True if deleted, False if it did not exist."""
    path = _template_path(name.strip(), template_dir)
    if not path.exists():
        return False
    path.unlink()
    return True


def instantiate_template(name: str, overrides: dict[str, Any] | None = None,
                         template_dir: Path = _DEFAULT_TEMPLATE_DIR) -> dict[str, Any]:
    """Create a new snapshot dict from a template, applying optional *overrides* per section."""
    base = load_template(name, template_dir)
    snapshot = copy.deepcopy(base)
    # Strip internal metadata so the result looks like a fresh snapshot
    snapshot.pop("_template_name", None)
    if overrides:
        for section, values in overrides.items():
            if isinstance(snapshot.get(section), dict) and isinstance(values, dict):
                snapshot[section].update(values)
            else:
                snapshot[section] = values
    return snapshot
