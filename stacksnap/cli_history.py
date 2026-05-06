"""CLI commands for snapshot access history."""

from __future__ import annotations

import argparse
from pathlib import Path

from stacksnap.history import (
    clear_history,
    get_history,
    most_accessed,
    record_access,
)


def _default_snapshot_dir() -> Path:
    return Path.home() / ".stacksnap" / "snapshots"


def cmd_history_log(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    entries = get_history(
        snap_dir,
        snapshot_id=getattr(args, "id", None),
        action=getattr(args, "action", None),
        limit=getattr(args, "limit", None),
    )
    if not entries:
        print("No history entries found.")
        return
    for e in entries:
        ts = e.get("timestamp", 0)
        print(f"{ts:.0f}  {e.get('action','?'):10}  {e.get('snapshot_id','?')}")


def cmd_history_record(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    entry = record_access(snap_dir, args.id, action=args.action)
    print(f"Recorded '{entry['action']}' for snapshot '{entry['snapshot_id']}'.")


def cmd_history_clear(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    sid = getattr(args, "id", None)
    removed = clear_history(snap_dir, snapshot_id=sid)
    target = f"snapshot '{sid}'" if sid else "all snapshots"
    print(f"Cleared {removed} history entry/entries for {target}.")


def cmd_history_top(args: argparse.Namespace) -> None:
    snap_dir = Path(args.snapshot_dir)
    top_n = getattr(args, "top", 5)
    results = most_accessed(snap_dir, top_n=top_n)
    if not results:
        print("No history recorded yet.")
        return
    for rank, (sid, count) in enumerate(results, 1):
        print(f"{rank}. {sid}  ({count} access{'es' if count != 1 else ''})")


def build_history_parser(
    parent: argparse._SubParsersAction | None = None,
    snapshot_dir: str | None = None,
) -> argparse.ArgumentParser:
    default_dir = snapshot_dir or str(_default_snapshot_dir())

    if parent is not None:
        parser = parent.add_parser("history", help="Snapshot access history")
    else:
        parser = argparse.ArgumentParser(prog="stacksnap-history")

    parser.add_argument("--snapshot-dir", default=default_dir)
    sub = parser.add_subparsers(dest="history_cmd", required=True)

    log_p = sub.add_parser("log", help="Show history entries")
    log_p.add_argument("--id", default=None, help="Filter by snapshot ID")
    log_p.add_argument("--action", default=None, help="Filter by action")
    log_p.add_argument("--limit", type=int, default=None)
    log_p.set_defaults(func=cmd_history_log)

    rec_p = sub.add_parser("record", help="Manually record an access event")
    rec_p.add_argument("id")
    rec_p.add_argument("--action", default="view")
    rec_p.set_defaults(func=cmd_history_record)

    clr_p = sub.add_parser("clear", help="Clear history entries")
    clr_p.add_argument("--id", default=None)
    clr_p.set_defaults(func=cmd_history_clear)

    top_p = sub.add_parser("top", help="Show most-accessed snapshots")
    top_p.add_argument("--top", type=int, default=5)
    top_p.set_defaults(func=cmd_history_top)

    return parser
