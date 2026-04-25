"""Main CLI entry-point for stacksnap."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stacksnap.snapshot import capture_snapshot, save_snapshot, load_snapshot, list_snapshots
from stacksnap.restore import restore_snapshot
from stacksnap.diff import diff_snapshots, format_diff
from stacksnap.cli_tags import build_tag_parser
from stacksnap.cli_schedule import build_schedule_parser
from stacksnap.cli_search import build_search_parser
from stacksnap.cli_pin import build_pin_parser
from stacksnap.cli_notes import build_notes_parser

_DEFAULT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_capture(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    snap = capture_snapshot(name=getattr(args, "name", None))
    path = save_snapshot(snap, snap_dir)
    print(f"Snapshot saved: {path}")


def cmd_restore(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    snap = load_snapshot(args.snapshot_id, snap_dir)
    warnings = restore_snapshot(snap)
    if warnings:
        for w in warnings:
            print(f"[warn] {w}", file=sys.stderr)
    else:
        print("Restore complete.")


def cmd_list(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    snaps = list_snapshots(snap_dir)
    if not snaps:
        print("No snapshots found.")
        return
    for s in snaps:
        print(s)


def cmd_diff(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    a = load_snapshot(args.snapshot_a, snap_dir)
    b = load_snapshot(args.snapshot_b, snap_dir)
    diff = diff_snapshots(a, b)
    print(format_diff(diff))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stacksnap", description="Capture and restore dev environment state.")
    sub = parser.add_subparsers(dest="command", required=True)

    cap = sub.add_parser("capture", help="Capture current environment")
    cap.add_argument("--name", default=None)
    cap.set_defaults(func=cmd_capture)

    res = sub.add_parser("restore", help="Restore a snapshot")
    res.add_argument("snapshot_id")
    res.set_defaults(func=cmd_restore)

    lst = sub.add_parser("list", help="List snapshots")
    lst.set_defaults(func=cmd_list)

    dif = sub.add_parser("diff", help="Diff two snapshots")
    dif.add_argument("snapshot_a")
    dif.add_argument("snapshot_b")
    dif.set_defaults(func=cmd_diff)

    build_tag_parser(sub)
    build_schedule_parser(sub)
    build_search_parser(sub)
    build_pin_parser(sub)
    build_notes_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
