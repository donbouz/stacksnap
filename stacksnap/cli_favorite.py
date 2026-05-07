"""CLI commands for managing favorite snapshots."""
from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.favorite import add_favorite, remove_favorite, is_favorite, get_favorites


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_favorite_add(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    added = add_favorite(args.snapshot_id, snap_dir)
    if added:
        print(f"Starred snapshot '{args.snapshot_id}'.")
    else:
        print(f"Snapshot '{args.snapshot_id}' is already starred.")


def cmd_favorite_remove(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    removed = remove_favorite(args.snapshot_id, snap_dir)
    if removed:
        print(f"Unstarred snapshot '{args.snapshot_id}'.")
    else:
        print(f"Snapshot '{args.snapshot_id}' was not starred.")


def cmd_favorite_list(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    favorites = get_favorites(snap_dir)
    if not favorites:
        print("No starred snapshots.")
        return
    for fav in favorites:
        print(fav)


def cmd_favorite_check(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    starred = is_favorite(args.snapshot_id, snap_dir)
    status = "starred" if starred else "not starred"
    print(f"Snapshot '{args.snapshot_id}' is {status}.")


def build_favorite_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = parent.add_parser("favorite", help="Manage starred snapshots")
    p.add_argument("--snapshot-dir", default=str(_default_snapshot_dir()))
    sub = p.add_subparsers(dest="favorite_cmd", required=True)

    add_p = sub.add_parser("add", help="Star a snapshot")
    add_p.add_argument("snapshot_id")
    add_p.set_defaults(func=cmd_favorite_add)

    rm_p = sub.add_parser("remove", help="Unstar a snapshot")
    rm_p.add_argument("snapshot_id")
    rm_p.set_defaults(func=cmd_favorite_remove)

    ls_p = sub.add_parser("list", help="List starred snapshots")
    ls_p.set_defaults(func=cmd_favorite_list)

    chk_p = sub.add_parser("check", help="Check if a snapshot is starred")
    chk_p.add_argument("snapshot_id")
    chk_p.set_defaults(func=cmd_favorite_check)
