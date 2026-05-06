"""CLI commands for snapshot summary."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.summary import summarise_snapshot_file


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_summary(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir) if getattr(args, "snapshot_dir", None) else _default_snapshot_dir()
    snapshot_path = snap_dir / f"{args.name}.json"
    try:
        output = summarise_snapshot_file(snapshot_path)
        print(output)
    except FileNotFoundError:
        print(f"[error] Snapshot '{args.name}' not found in {snap_dir}")


def build_summary_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    if subparsers is not None:
        parser = subparsers.add_parser("summary", help="Print a summary of a snapshot")
    else:
        parser = argparse.ArgumentParser(prog="stacksnap-summary", description="Print a snapshot summary")

    parser.add_argument("name", help="Snapshot name (without .json extension)")
    parser.add_argument(
        "--snapshot-dir",
        dest="snapshot_dir",
        default=None,
        help="Directory containing snapshots (default: ~/.stacksnap/snapshots)",
    )
    parser.set_defaults(func=cmd_summary)
    return parser


if __name__ == "__main__":  # pragma: no cover
    _parser = build_summary_parser()
    _args = _parser.parse_args()
    _args.func(_args)
