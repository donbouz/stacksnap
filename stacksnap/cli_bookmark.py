"""CLI commands for managing snapshot bookmarks."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_bookmark_set(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    is_new = set_bookmark(snap_dir, args.name, args.snapshot_id)
    verb = "Created" if is_new else "Updated"
    print(f"{verb} bookmark '{args.name}' -> {args.snapshot_id}")


def cmd_bookmark_remove(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    removed = remove_bookmark(snap_dir, args.name)
    if removed:
        print(f"Removed bookmark '{args.name}'.")
    else:
        print(f"Bookmark '{args.name}' not found.")


def cmd_bookmark_resolve(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    snapshot_id = resolve_bookmark(snap_dir, args.name)
    if snapshot_id is None:
        print(f"No bookmark named '{args.name}'.")
    else:
        print(snapshot_id)


def cmd_bookmark_list(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", None) or _default_snapshot_dir())
    bookmarks = list_bookmarks(snap_dir)
    if not bookmarks:
        print("No bookmarks defined.")
        return
    for bm in bookmarks:
        print(f"{bm['name']:20s}  {bm['snapshot_id']}")


def build_bookmark_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("bookmark", help="Manage snapshot bookmarks")
    sub = p.add_subparsers(dest="bookmark_cmd", required=True)

    ps = sub.add_parser("set", help="Create or update a bookmark")
    ps.add_argument("name", help="Bookmark name")
    ps.add_argument("snapshot_id", help="Snapshot ID to bookmark")
    ps.set_defaults(func=cmd_bookmark_set)

    pr = sub.add_parser("remove", help="Remove a bookmark")
    pr.add_argument("name", help="Bookmark name")
    pr.set_defaults(func=cmd_bookmark_remove)

    pres = sub.add_parser("resolve", help="Resolve a bookmark to its snapshot ID")
    pres.add_argument("name", help="Bookmark name")
    pres.set_defaults(func=cmd_bookmark_resolve)

    pl = sub.add_parser("list", help="List all bookmarks")
    pl.set_defaults(func=cmd_bookmark_list)
