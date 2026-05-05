"""CLI commands for the watchlist feature."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.watchlist import (
    add_to_watchlist,
    clear_watchlist,
    get_watchlist,
    is_watched,
    remove_from_watchlist,
)

_DEFAULT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_watch_add(args: argparse.Namespace) -> None:
    directory = Path(getattr(args, "directory", _DEFAULT_DIR))
    added = add_to_watchlist(directory, args.snapshot_id, args.reason or "")
    if added:
        print(f"Watching: {args.snapshot_id}")
    else:
        print(f"Already watched: {args.snapshot_id}")


def cmd_watch_remove(args: argparse.Namespace) -> None:
    directory = Path(getattr(args, "directory", _DEFAULT_DIR))
    removed = remove_from_watchlist(directory, args.snapshot_id)
    if removed:
        print(f"Removed from watchlist: {args.snapshot_id}")
    else:
        print(f"Not in watchlist: {args.snapshot_id}")


def cmd_watch_list(args: argparse.Namespace) -> None:
    directory = Path(getattr(args, "directory", _DEFAULT_DIR))
    entries = get_watchlist(directory)
    if not entries:
        print("Watchlist is empty.")
        return
    for sid, meta in entries.items():
        reason = meta.get("reason", "")
        suffix = f"  # {reason}" if reason else ""
        print(f"  {sid}{suffix}")


def cmd_watch_check(args: argparse.Namespace) -> None:
    directory = Path(getattr(args, "directory", _DEFAULT_DIR))
    watched = is_watched(directory, args.snapshot_id)
    status = "watched" if watched else "not watched"
    print(f"{args.snapshot_id}: {status}")


def cmd_watch_clear(args: argparse.Namespace) -> None:
    directory = Path(getattr(args, "directory", _DEFAULT_DIR))
    count = clear_watchlist(directory)
    print(f"Cleared {count} entr{'y' if count == 1 else 'ies'} from watchlist.")


def build_watchlist_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("watch", help="Manage the snapshot watchlist")
    sub = p.add_subparsers(dest="watch_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a snapshot to the watchlist")
    add_p.add_argument("snapshot_id")
    add_p.add_argument("--reason", default="", help="Optional reason for watching")
    add_p.set_defaults(func=cmd_watch_add)

    rm_p = sub.add_parser("remove", help="Remove a snapshot from the watchlist")
    rm_p.add_argument("snapshot_id")
    rm_p.set_defaults(func=cmd_watch_remove)

    ls_p = sub.add_parser("list", help="List all watched snapshots")
    ls_p.set_defaults(func=cmd_watch_list)

    chk_p = sub.add_parser("check", help="Check if a snapshot is watched")
    chk_p.add_argument("snapshot_id")
    chk_p.set_defaults(func=cmd_watch_check)

    clr_p = sub.add_parser("clear", help="Clear the entire watchlist")
    clr_p.set_defaults(func=cmd_watch_clear)
