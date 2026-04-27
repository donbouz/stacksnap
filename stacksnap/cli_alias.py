"""CLI commands for snapshot aliases."""

import argparse
from pathlib import Path

from stacksnap.alias import set_alias, remove_alias, resolve_alias, list_aliases

_DEFAULT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_alias_set(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    is_new = set_alias(snap_dir, args.alias, args.snapshot_id)
    verb = "Created" if is_new else "Updated"
    print(f"{verb} alias '{args.alias}' -> {args.snapshot_id}")


def cmd_alias_remove(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    removed = remove_alias(snap_dir, args.alias)
    if removed:
        print(f"Removed alias '{args.alias}'.")
    else:
        print(f"Alias '{args.alias}' not found.")


def cmd_alias_resolve(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    snapshot_id = resolve_alias(snap_dir, args.alias)
    if snapshot_id:
        print(snapshot_id)
    else:
        print(f"No alias named '{args.alias}'.")


def cmd_alias_list(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    entries = list_aliases(snap_dir)
    if not entries:
        print("No aliases defined.")
        return
    for entry in entries:
        print(f"{entry['alias']:30s} -> {entry['snapshot_id']}")


def build_alias_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("alias", help="Manage snapshot aliases")
    sub = p.add_subparsers(dest="alias_cmd", required=True)

    p_set = sub.add_parser("set", help="Create or update an alias")
    p_set.add_argument("alias", help="Alias name")
    p_set.add_argument("snapshot_id", help="Snapshot ID to map to")
    p_set.set_defaults(func=cmd_alias_set)

    p_rm = sub.add_parser("remove", help="Delete an alias")
    p_rm.add_argument("alias", help="Alias name to remove")
    p_rm.set_defaults(func=cmd_alias_remove)

    p_res = sub.add_parser("resolve", help="Print snapshot ID for an alias")
    p_res.add_argument("alias", help="Alias name to resolve")
    p_res.set_defaults(func=cmd_alias_resolve)

    p_ls = sub.add_parser("list", help="List all aliases")
    p_ls.set_defaults(func=cmd_alias_list)
