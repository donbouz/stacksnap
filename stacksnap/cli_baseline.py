"""CLI commands for baseline management."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap import baseline as bl


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_baseline_set(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    changed = bl.set_baseline(args.snapshot_id, snap_dir)
    if changed:
        print(f"Baseline set to: {args.snapshot_id}")
    else:
        print(f"Baseline already set to: {args.snapshot_id}")


def cmd_baseline_get(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    current = bl.get_baseline(snap_dir)
    if current:
        print(f"Current baseline: {current}")
    else:
        print("No baseline is set.")


def cmd_baseline_clear(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    removed = bl.clear_baseline(snap_dir)
    if removed:
        print("Baseline cleared.")
    else:
        print("No baseline was set.")


def cmd_baseline_diff(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    try:
        diff = bl.diff_against_baseline(args.snapshot_id, snap_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return

    if not diff["sections"]:
        print(f"No differences between baseline '{diff['baseline']}' and '{diff['target']}'.")
        return

    print(f"Diff: {diff['baseline']} (baseline) vs {diff['target']}")
    for section, changes in diff["sections"].items():
        print(f"  [{section}]")
        print(f"    baseline : {changes['baseline']}")
        print(f"    target   : {changes['target']}")


def build_baseline_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("baseline", help="Manage the project baseline snapshot")
    sp = p.add_subparsers(dest="baseline_cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--snapshot-dir", default=str(_default_snapshot_dir()))

    s = sp.add_parser("set", parents=[common], help="Set a snapshot as the baseline")
    s.add_argument("snapshot_id")
    s.set_defaults(func=cmd_baseline_set)

    g = sp.add_parser("get", parents=[common], help="Show the current baseline")
    g.set_defaults(func=cmd_baseline_get)

    c = sp.add_parser("clear", parents=[common], help="Clear the baseline")
    c.set_defaults(func=cmd_baseline_clear)

    d = sp.add_parser("diff", parents=[common], help="Diff a snapshot against the baseline")
    d.add_argument("snapshot_id")
    d.set_defaults(func=cmd_baseline_diff)
