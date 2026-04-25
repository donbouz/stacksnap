"""CLI sub-commands for snapshot notes."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.notes import add_note, get_notes, delete_notes, format_notes

_DEFAULT_DIR = Path.home() / ".stacksnap" / "snapshots"


def cmd_note_add(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    entry = add_note(args.snapshot_id, args.text, snap_dir)
    print(f"Note added at {entry['timestamp']}.")


def cmd_note_list(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    entries = get_notes(args.snapshot_id, snap_dir)
    print(format_notes(args.snapshot_id, entries))


def cmd_note_delete(args: argparse.Namespace) -> None:
    snap_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))
    removed = delete_notes(args.snapshot_id, snap_dir)
    if removed:
        print(f"All notes for '{args.snapshot_id}' deleted.")
    else:
        print(f"No notes found for '{args.snapshot_id}'.")


def build_notes_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("notes", help="Manage notes on snapshots")
    sp = p.add_subparsers(dest="notes_cmd", required=True)

    # add
    pa = sp.add_parser("add", help="Add a note to a snapshot")
    pa.add_argument("snapshot_id")
    pa.add_argument("text", help="Note text")
    pa.set_defaults(func=cmd_note_add)

    # list
    pl = sp.add_parser("list", help="List notes for a snapshot")
    pl.add_argument("snapshot_id")
    pl.set_defaults(func=cmd_note_list)

    # delete
    pd = sp.add_parser("delete", help="Delete all notes for a snapshot")
    pd.add_argument("snapshot_id")
    pd.set_defaults(func=cmd_note_delete)
