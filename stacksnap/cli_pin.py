"""CLI commands for pinning/unpinning snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.pin import pin_snapshot, unpin_snapshot, is_pinned, list_pinned

_DEFAULT_DIR = Path.home() / ".stacksnap"


def cmd_pin(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    label: str = args.label
    if pin_snapshot(snap_dir, label):
        print(f"Pinned snapshot '{label}'.")
    else:
        print(f"Snapshot '{label}' is already pinned.")


def cmd_unpin(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    label: str = args.label
    if unpin_snapshot(snap_dir, label):
        print(f"Unpinned snapshot '{label}'.")
    else:
        print(f"Snapshot '{label}' was not pinned.")


def cmd_pin_list(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    pins = list_pinned(snap_dir)
    if not pins:
        print("No pinned snapshots.")
    else:
        print("Pinned snapshots:")
        for label in pins:
            print(f"  - {label}")


def cmd_pin_check(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    label: str = args.label
    status = "pinned" if is_pinned(snap_dir, label) else "not pinned"
    print(f"Snapshot '{label}' is {status}.")


def build_pin_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("pin", help="Pin/unpin snapshots")
    sub = p.add_subparsers(dest="pin_cmd", required=True)

    p_add = sub.add_parser("add", help="Pin a snapshot")
    p_add.add_argument("label")
    p_add.set_defaults(func=cmd_pin)

    p_rm = sub.add_parser("remove", help="Unpin a snapshot")
    p_rm.add_argument("label")
    p_rm.set_defaults(func=cmd_unpin)

    p_ls = sub.add_parser("list", help="List pinned snapshots")
    p_ls.set_defaults(func=cmd_pin_list)

    p_chk = sub.add_parser("check", help="Check if a snapshot is pinned")
    p_chk.add_argument("label")
    p_chk.set_defaults(func=cmd_pin_check)
