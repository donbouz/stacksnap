"""Export and import snapshots to/from portable archive files.

Allows sharing environment snapshots across machines or teams by
packing snapshot JSON into a compressed tarball (.snap.tar.gz).
"""

import json
import os
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from stacksnap.snapshot import load_snapshot, save_snapshot, SNAPSHOT_DIR


DEFAULT_EXPORT_DIR = Path.cwd()


def export_snapshot(
    label: str,
    output_dir: Optional[Path] = None,
    snapshot_dir: Optional[Path] = None,
) -> Path:
    """Export a named snapshot to a portable .snap.tar.gz archive.

    Args:
        label: The snapshot label to export.
        output_dir: Directory where the archive will be written.
                    Defaults to the current working directory.
        snapshot_dir: Override the default snapshot storage directory.

    Returns:
        Path to the created archive file.

    Raises:
        FileNotFoundError: If no snapshot with the given label exists.
    """
    snap_dir = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR
    output_dir = Path(output_dir) if output_dir else DEFAULT_EXPORT_DIR

    snapshot = load_snapshot(label, snapshot_dir=snap_dir)
    if snapshot is None:
        raise FileNotFoundError(f"Snapshot '{label}' not found in {snap_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Sanitise label for use in a filename
    safe_label = label.replace(" ", "_").replace("/", "-")
    archive_name = f"{safe_label}.snap.tar.gz"
    archive_path = output_dir / archive_name

    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / f"{safe_label}.json"
        json_path.write_text(json.dumps(snapshot, indent=2))

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(json_path, arcname=f"{safe_label}.json")

    return archive_path


def import_snapshot(
    archive_path: Path,
    snapshot_dir: Optional[Path] = None,
    overwrite: bool = False,
) -> str:
    """Import a snapshot from a .snap.tar.gz archive.

    Args:
        archive_path: Path to the archive file produced by export_snapshot.
        snapshot_dir: Override the default snapshot storage directory.
        overwrite: If True, replace an existing snapshot with the same label.

    Returns:
        The label of the imported snapshot.

    Raises:
        FileNotFoundError: If the archive does not exist.
        ValueError: If the archive contains no recognisable snapshot JSON,
                    or if the snapshot already exists and overwrite is False.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    snap_dir = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive_path, "r:gz") as tar:
            json_members = [
                m for m in tar.getmembers() if m.name.endswith(".json")
            ]
            if not json_members:
                raise ValueError(
                    f"Archive '{archive_path}' contains no snapshot JSON file."
                )
            tar.extractall(tmp, members=json_members)

        json_file = Path(tmp) / json_members[0].name
        snapshot = json.loads(json_file.read_text())

    label = snapshot.get("label")
    if not label:
        raise ValueError("Snapshot JSON is missing a 'label' field.")

    existing = load_snapshot(label, snapshot_dir=snap_dir)
    if existing is not None and not overwrite:
        raise ValueError(
            f"Snapshot '{label}' already exists. Use overwrite=True to replace it."
        )

    # Record when the snapshot was imported
    snapshot["imported_at"] = datetime.utcnow().isoformat()
    save_snapshot(snapshot, snapshot_dir=snap_dir)

    return label
