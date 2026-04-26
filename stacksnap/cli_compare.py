"""CLI commands for comparing two snapshots by similarity score."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stacksnap.compare import compare_snapshots, format_compare
from stacksnap.snapshot import load_snapshot


def cmd_compare(args: argparse.Namespace, snapshot_dir: Path | None = None) -> None:
    """Load two snapshots and print a formatted similarity report.

    Args:
        args: Parsed CLI arguments.  Must expose ``snap_a`` and ``snap_b``
              (snapshot IDs / filenames without extension) and optionally
              ``snapshot_dir``.
        snapshot_dir: Override the directory used to locate snapshots.  Useful
                      for testing without touching the real store.
    """
    base_dir = snapshot_dir or _default_snapshot_dir()

    path_a = base_dir / f"{args.snap_a}.json"
    path_b = base_dir / f"{args.snap_b}.json"

    missing = [p for p in (path_a, path_b) if not p.exists()]
    if missing:
        for p in missing:
            print(f"Error: snapshot not found — {p.name}", file=sys.stderr)
        sys.exit(1)

    snap_a = load_snapshot(path_a)
    snap_b = load_snapshot(path_b)

    result = compare_snapshots(snap_a, snap_b)
    print(format_compare(result))


def cmd_compare_all(args: argparse.Namespace, snapshot_dir: Path | None = None) -> None:
    """Compare a single snapshot against every other snapshot in the store.

    Prints a ranked table of similarity scores (highest first).

    Args:
        args: Parsed CLI arguments.  Must expose ``snap_id``.
        snapshot_dir: Override the directory used to locate snapshots.
    """
    base_dir = snapshot_dir or _default_snapshot_dir()

    target_path = base_dir / f"{args.snap_id}.json"
    if not target_path.exists():
        print(f"Error: snapshot not found — {target_path.name}", file=sys.stderr)
        sys.exit(1)

    target = load_snapshot(target_path)

    candidates = [
        p for p in sorted(base_dir.glob("*.json")) if p.name != target_path.name
    ]

    if not candidates:
        print("No other snapshots available for comparison.")
        return

    results: list[tuple[str, float]] = []
    for path in candidates:
        snap = load_snapshot(path)
        result = compare_snapshots(target, snap)
        # Overall score is the mean of per-section scores
        scores = [v["score"] for v in result.get("sections", {}).values()]
        overall = sum(scores) / len(scores) if scores else 0.0
        results.append((path.stem, overall))

    results.sort(key=lambda t: t[1], reverse=True)

    label = target.get("label", args.snap_id)
    print(f"Similarity ranking for '{label}':\n")
    print(f"  {'Snapshot':<40}  {'Score':>6}")
    print(f"  {'-' * 40}  {'-' * 6}")
    for name, score in results:
        print(f"  {name:<40}  {score:>5.1%}")


def _default_snapshot_dir() -> Path:
    """Return the default directory where snapshots are stored."""
    return Path.home() / ".stacksnap" / "snapshots"


def build_compare_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register *compare* sub-commands onto *subparsers*.

    Two commands are registered:

    * ``compare <snap_a> <snap_b>`` — detailed side-by-side similarity report.
    * ``compare-all <snap_id>``     — rank all snapshots by similarity to one.
    """
    # compare <a> <b>
    p_cmp = subparsers.add_parser(
        "compare",
        help="Compare two snapshots and show a similarity score breakdown.",
    )
    p_cmp.add_argument("snap_a", help="ID of the first snapshot.")
    p_cmp.add_argument("snap_b", help="ID of the second snapshot.")
    p_cmp.set_defaults(func=cmd_compare)

    # compare-all <snap_id>
    p_all = subparsers.add_parser(
        "compare-all",
        help="Rank all stored snapshots by similarity to a given snapshot.",
    )
    p_all.add_argument("snap_id", help="ID of the reference snapshot.")
    p_all.set_defaults(func=cmd_compare_all)
