"""CLI sub-commands for snapshot archiving and purging."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.archive import archive_snapshots, purge_archive

DEFAULT_SNAPSHOT_DIR = Path.home() / ".stacksnap" / "snapshots"
DEFAULT_ARCHIVE_DIR = Path.home() / ".stacksnap" / "archive"


def cmd_archive(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else DEFAULT_SNAPSHOT_DIR
    archive_dir = Path(args.archive_dir) if args.archive_dir else DEFAULT_ARCHIVE_DIR

    archived = archive_snapshots(
        snapshot_dir=snapshot_dir,
        archive_dir=archive_dir,
        max_age_days=args.max_age_days,
        keep_pinned=not args.include_pinned,
    )
    if archived:
        print(f"Archived {len(archived)} snapshot(s):")
        for name in archived:
            print(f"  - {name}")
    else:
        print("No snapshots eligible for archiving.")


def cmd_purge(args: argparse.Namespace) -> None:
    archive_dir = Path(args.archive_dir) if args.archive_dir else DEFAULT_ARCHIVE_DIR

    purged = purge_archive(
        archive_dir=archive_dir,
        older_than_days=args.older_than_days,
    )
    if purged:
        print(f"Purged {len(purged)} archived snapshot(s):")
        for name in purged:
            print(f"  - {name}")
    else:
        print("Nothing to purge.")


def build_archive_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_archive = subparsers.add_parser("archive", help="Move old snapshots to archive")
    p_archive.add_argument("--max-age-days", type=int, default=30, dest="max_age_days")
    p_archive.add_argument("--include-pinned", action="store_true", dest="include_pinned")
    p_archive.add_argument("--snapshot-dir", default=None, dest="snapshot_dir")
    p_archive.add_argument("--archive-dir", default=None, dest="archive_dir")
    p_archive.set_defaults(func=cmd_archive)

    p_purge = subparsers.add_parser("purge", help="Permanently delete old archived snapshots")
    p_purge.add_argument("--older-than-days", type=int, default=90, dest="older_than_days")
    p_purge.add_argument("--archive-dir", default=None, dest="archive_dir")
    p_purge.set_defaults(func=cmd_purge)
