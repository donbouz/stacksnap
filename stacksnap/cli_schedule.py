"""CLI commands for managing scheduled snapshots."""

import argparse
import sys
from pathlib import Path

from stacksnap.schedule import (
    add_schedule,
    remove_schedule,
    list_schedules,
    get_schedule,
    is_due,
)
from stacksnap.snapshot import capture_snapshot, save_snapshot


def cmd_schedule_add(args: argparse.Namespace) -> None:
    entry = add_schedule(
        project=args.project,
        interval_minutes=args.interval,
        label_prefix=args.prefix,
    )
    print(
        f"Scheduled '{entry['project']}' every {entry['interval_minutes']} min "
        f"(prefix: {entry['label_prefix']})"
    )


def cmd_schedule_remove(args: argparse.Namespace) -> None:
    removed = remove_schedule(args.project)
    if removed:
        print(f"Removed schedule for '{args.project}'.")
    else:
        print(f"No schedule found for '{args.project}'.")
        sys.exit(1)


def cmd_schedule_list(args: argparse.Namespace) -> None:
    entries = list_schedules()
    if not entries:
        print("No schedules configured.")
        return
    for e in entries:
        last = e["last_run"] or "never"
        print(
            f"  {e['project']}: every {e['interval_minutes']} min, "
            f"last run: {last}, prefix: {e['label_prefix']}"
        )


def cmd_schedule_run(args: argparse.Namespace) -> None:
    """Trigger a snapshot for project if it is due."""
    if not is_due(args.project):
        print(f"'{args.project}' is not due yet. Skipping.")
        return
    entry = get_schedule(args.project)
    snap = capture_snapshot(name=f"{entry['label_prefix']}-{args.project}")
    path = save_snapshot(snap)
    from stacksnap.schedule import mark_ran
    mark_ran(args.project)
    print(f"Snapshot saved: {path}")


def build_schedule_parser(subparsers=None):
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="stacksnap-schedule")
        sub = parser.add_subparsers(dest="schedule_cmd")
    else:
        parser = subparsers.add_parser("schedule", help="Manage scheduled snapshots")
        sub = parser.add_subparsers(dest="schedule_cmd")

    p_add = sub.add_parser("add", help="Add a schedule")
    p_add.add_argument("project", help="Project name")
    p_add.add_argument("interval", type=int, help="Interval in minutes")
    p_add.add_argument("--prefix", default="auto", help="Label prefix")
    p_add.set_defaults(func=cmd_schedule_add)

    p_rm = sub.add_parser("remove", help="Remove a schedule")
    p_rm.add_argument("project", help="Project name")
    p_rm.set_defaults(func=cmd_schedule_remove)

    p_ls = sub.add_parser("list", help="List schedules")
    p_ls.set_defaults(func=cmd_schedule_list)

    p_run = sub.add_parser("run", help="Run snapshot if due")
    p_run.add_argument("project", help="Project name")
    p_run.set_defaults(func=cmd_schedule_run)

    return parser
