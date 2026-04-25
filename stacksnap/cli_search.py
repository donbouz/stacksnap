"""CLI sub-commands for snapshot search."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.search import format_search_results, search_snapshots

DEFAULT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_search(args: argparse.Namespace) -> None:
    """Handle the ``stacksnap search`` command."""
    snapshots_dir = Path(getattr(args, "snapshots_dir", DEFAULT_DIR))

    results = search_snapshots(
        snapshots_dir,
        query=args.query or None,
        tag=args.tag or None,
        python_version=args.python or None,
        node_version=args.node or None,
    )

    print(format_search_results(results))


def build_search_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """Register the ``search`` sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "search",
        help="Search snapshots by metadata, tag, or version.",
    )
    p.add_argument(
        "query",
        nargs="?",
        default="",
        help="Free-text substring to search across all snapshot fields.",
    )
    p.add_argument(
        "--tag",
        default="",
        metavar="TAG",
        help="Filter to snapshots carrying this tag.",
    )
    p.add_argument(
        "--python",
        default="",
        metavar="VERSION",
        help="Filter by Python version substring (e.g. '3.11').",
    )
    p.add_argument(
        "--node",
        default="",
        metavar="VERSION",
        help="Filter by Node version substring (e.g. '20').",
    )
    p.set_defaults(func=cmd_search)
