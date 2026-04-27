"""Manage human-friendly aliases for snapshot IDs."""

import json
from pathlib import Path
from typing import Dict, List, Optional

_ALIAS_FILE = "aliases.json"


def _load_aliases(snapshot_dir: Path) -> Dict[str, str]:
    path = snapshot_dir / _ALIAS_FILE
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_aliases(snapshot_dir: Path, aliases: Dict[str, str]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_dir / _ALIAS_FILE
    with path.open("w") as fh:
        json.dump(aliases, fh, indent=2)


def set_alias(snapshot_dir: Path, alias: str, snapshot_id: str) -> bool:
    """Map *alias* to *snapshot_id*. Returns True if alias was new."""
    if not alias or not alias.strip():
        raise ValueError("Alias must not be empty.")
    aliases = _load_aliases(snapshot_dir)
    is_new = alias not in aliases
    aliases[alias] = snapshot_id
    _save_aliases(snapshot_dir, aliases)
    return is_new


def remove_alias(snapshot_dir: Path, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed."""
    aliases = _load_aliases(snapshot_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(snapshot_dir, aliases)
    return True


def resolve_alias(snapshot_dir: Path, alias: str) -> Optional[str]:
    """Return the snapshot_id for *alias*, or None if not found."""
    return _load_aliases(snapshot_dir).get(alias)


def list_aliases(snapshot_dir: Path) -> List[Dict[str, str]]:
    """Return all aliases as a list of {alias, snapshot_id} dicts."""
    aliases = _load_aliases(snapshot_dir)
    return [{"alias": k, "snapshot_id": v} for k, v in sorted(aliases.items())]
