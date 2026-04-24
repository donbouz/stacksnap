"""Tag management for snapshots — add, remove, and filter by tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

TAGS_FILE = "tags.json"


def _load_tags_index(snapshot_dir: Path) -> dict:
    tags_path = snapshot_dir / TAGS_FILE
    if tags_path.exists():
        return json.loads(tags_path.read_text())
    return {}


def _save_tags_index(snapshot_dir: Path, index: dict) -> None:
    tags_path = snapshot_dir / TAGS_FILE
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    tags_path.write_text(json.dumps(index, indent=2))


def add_tag(snapshot_dir: Path, snapshot_name: str, tag: str) -> None:
    """Add a tag to a snapshot."""
    index = _load_tags_index(snapshot_dir)
    tags = index.get(snapshot_name, [])
    if tag not in tags:
        tags.append(tag)
    index[snapshot_name] = tags
    _save_tags_index(snapshot_dir, index)


def remove_tag(snapshot_dir: Path, snapshot_name: str, tag: str) -> bool:
    """Remove a tag from a snapshot. Returns True if tag was present."""
    index = _load_tags_index(snapshot_dir)
    tags = index.get(snapshot_name, [])
    if tag not in tags:
        return False
    tags.remove(tag)
    index[snapshot_name] = tags
    _save_tags_index(snapshot_dir, index)
    return True


def get_tags(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return all tags for a given snapshot."""
    index = _load_tags_index(snapshot_dir)
    return index.get(snapshot_name, [])


def find_by_tag(snapshot_dir: Path, tag: str) -> List[str]:
    """Return snapshot names that carry the given tag."""
    index = _load_tags_index(snapshot_dir)
    return [name for name, tags in index.items() if tag in tags]


def list_all_tags(snapshot_dir: Path) -> dict:
    """Return the full tags index {snapshot_name: [tags]}."""
    return _load_tags_index(snapshot_dir)


def rename_snapshot_tags(snapshot_dir: Path, old_name: str, new_name: str) -> None:
    """Migrate tags when a snapshot is renamed."""
    index = _load_tags_index(snapshot_dir)
    if old_name in index:
        index[new_name] = index.pop(old_name)
        _save_tags_index(snapshot_dir, index)


def purge_snapshot_tags(snapshot_dir: Path, snapshot_name: str) -> None:
    """Remove all tag entries for a deleted snapshot."""
    index = _load_tags_index(snapshot_dir)
    if snapshot_name in index:
        del index[snapshot_name]
        _save_tags_index(snapshot_dir, index)
