"""CLI commands for renaming and relabelling snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.label import relabel_snapshot, rename_snapshot


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_rename(args: argparse.Namespace) -> None:
    """Rename a snapshot file and update its embedded label."""
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    result = rename_snapshot(
        snap_dir,
        args.old_name,
        args.new_name,
        overwrite=getattr(args, "overwrite", False),
    )
    if result["ok"]:
        print(f"renamed: {args.old_name} -> {args.new_name}")
    else:
        print(f"error: {result['reason']}")


def cmd_relabel(args: argparse.Namespace) -> None:
    """Update only the human-readable label inside a snapshot."""
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    result = relabel_snapshot(snap_dir, args.name, args.label)
    if result["ok"]:
        old = result.get("old_label", "(none)")
        print(f"relabelled '{args.name}': '{old}' -> '{args.label}'")
    else:
        print(f"error: {result['reason']}")


def build_label_parser(
    subparsers: argparse._SubParsersAction | None = None,
) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="stacksnap-label")
        sub = parser.add_subparsers(dest="label_cmd")
    else:
        parser = subparsers.add_parser("label", help="rename or relabel snapshots")
        sub = parser.add_subparsers(dest="label_cmd")

    # rename sub-command
    p_rename = sub.add_parser("rename", help="rename snapshot file and update embedded label")
    p_rename.add_argument("old_name", help="current snapshot name")
    p_rename.add_argument("new_name", help="desired new name")
    p_rename.add_argument("--overwrite", action="store_true", help="replace existing snapshot with new_name")
    p_rename.add_argument("--snapshot-dir", dest="snapshot_dir", default=None)
    p_rename.set_defaults(func=cmd_rename)

    # relabel sub-command
    p_relabel = sub.add_parser("relabel", help="update only the embedded label string")
    p_relabel.add_argument("name", help="snapshot name (file stem)")
    p_relabel.add_argument("label", help="new human-readable label")
    p_relabel.add_argument("--snapshot-dir", dest="snapshot_dir", default=None)
    p_relabel.set_defaults(func=cmd_relabel)

    return parser
