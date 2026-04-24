"""CLI sub-commands for snapshot tag management."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.tags import (
    add_tag,
    remove_tag,
    get_tags,
    find_by_tag,
    list_all_tags,
)

DEFAULT_SNAPSHOT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_tag_add(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    add_tag(snap_dir, args.snapshot, args.tag)
    print(f"Tagged '{args.snapshot}' with '{args.tag}'.")


def cmd_tag_remove(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    removed = remove_tag(snap_dir, args.snapshot, args.tag)
    if removed:
        print(f"Removed tag '{args.tag}' from '{args.snapshot}'.")
    else:
        print(f"Tag '{args.tag}' not found on '{args.snapshot}'.")


def cmd_tag_list(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    if args.snapshot:
        tags = get_tags(snap_dir, args.snapshot)
        if tags:
            print(f"Tags for '{args.snapshot}': {', '.join(tags)}")
        else:
            print(f"No tags for '{args.snapshot}'.")
    else:
        index = list_all_tags(snap_dir)
        if not index:
            print("No tags defined.")
            return
        for snap, tags in sorted(index.items()):
            print(f"  {snap}: {', '.join(tags)}")


def cmd_tag_find(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    matches = find_by_tag(snap_dir, args.tag)
    if matches:
        print(f"Snapshots tagged '{args.tag}':")
        for name in sorted(matches):
            print(f"  {name}")
    else:
        print(f"No snapshots found with tag '{args.tag}'.")


def build_tag_parser(subparsers, snapshot_dir: str = str(DEFAULT_SNAPSHOT_DIR)):
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_parser.add_argument(
        "--snapshot-dir", default=snapshot_dir, help="Snapshot storage directory"
    )
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    p_add.add_argument("snapshot", help="Snapshot name")
    p_add.add_argument("tag", help="Tag to add")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name")
    p_rm.add_argument("tag", help="Tag to remove")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List tags")
    p_ls.add_argument("snapshot", nargs="?", default=None, help="Optional snapshot name")
    p_ls.set_defaults(func=cmd_tag_list)

    p_find = tag_sub.add_parser("find", help="Find snapshots by tag")
    p_find.add_argument("tag", help="Tag to search for")
    p_find.set_defaults(func=cmd_tag_find)

    return tag_parser
