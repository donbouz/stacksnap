"""Minimal CLI entry-point for stacksnap."""

from __future__ import annotations

import argparse
import sys

from stacksnap.diff import diff_snapshots, format_diff
from stacksnap.snapshot import (
    capture_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from stacksnap.restore import restore_snapshot


def cmd_capture(args: argparse.Namespace) -> int:
    snap = capture_snapshot(name=args.name or None)
    path = save_snapshot(snap, directory=args.dir)
    print(f"Snapshot saved: {path}")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    snap = load_snapshot(args.label, directory=args.dir)
    warnings = restore_snapshot(snap)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("Restore complete with no warnings.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    snapshots = list_snapshots(directory=args.dir)
    if not snapshots:
        print("No snapshots found.")
        return 0
    for label, ts in snapshots:
        print(f"  {label}  ({ts})")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    snap_a = load_snapshot(args.label_a, directory=args.dir)
    snap_b = load_snapshot(args.label_b, directory=args.dir)
    diff = diff_snapshots(snap_a, snap_b)
    print(format_diff(diff))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stacksnap",
        description="Capture and restore local dev environment state.",
    )
    parser.add_argument(
        "--dir", default=".snapshots", help="Snapshot storage directory."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_capture = sub.add_parser("capture", help="Capture current environment.")
    p_capture.add_argument("--name", default="", help="Optional snapshot label.")

    p_restore = sub.add_parser("restore", help="Restore a saved snapshot.")
    p_restore.add_argument("label", help="Snapshot label to restore.")

    sub.add_parser("list", help="List saved snapshots.")

    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("label_a", help="Baseline snapshot label.")
    p_diff.add_argument("label_b", help="Target snapshot label.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "capture": cmd_capture,
        "restore": cmd_restore,
        "list": cmd_list,
        "diff": cmd_diff,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
