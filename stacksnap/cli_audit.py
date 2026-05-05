"""CLI commands for the audit log."""

from __future__ import annotations

import argparse
import json

from stacksnap.audit import clear_events, get_events, record_event


def cmd_audit_log(args: argparse.Namespace) -> None:
    """Print audit events, optionally filtered."""
    events = get_events(
        snapshot_id=getattr(args, "snapshot_id", None) or None,
        action=getattr(args, "action", None) or None,
        audit_file=getattr(args, "audit_file", None),
    )
    if not events:
        print("No audit events found.")
        return
    for ev in events:
        print(json.dumps(ev))


def cmd_audit_record(args: argparse.Namespace) -> None:
    """Manually record an audit event (useful for scripting)."""
    entry = record_event(
        action=args.action,
        snapshot_id=args.snapshot_id,
        details=json.loads(args.details) if getattr(args, "details", None) else None,
        audit_file=getattr(args, "audit_file", None),
    )
    print(f"Recorded: {entry['action']} for {entry['snapshot_id']} at {entry['timestamp']}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    """Clear all audit events."""
    removed = clear_events(audit_file=getattr(args, "audit_file", None))
    print(f"Cleared {removed} audit event(s).")


def build_audit_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    audit_p = subparsers.add_parser("audit", help="Audit log commands")
    audit_sub = audit_p.add_subparsers(dest="audit_cmd", required=True)

    # log
    log_p = audit_sub.add_parser("log", help="Print audit events")
    log_p.add_argument("--snapshot-id", dest="snapshot_id", default=None)
    log_p.add_argument("--action", default=None)
    log_p.add_argument("--audit-file", dest="audit_file", default=None)
    log_p.set_defaults(func=cmd_audit_log)

    # record
    rec_p = audit_sub.add_parser("record", help="Manually record an event")
    rec_p.add_argument("action")
    rec_p.add_argument("snapshot_id")
    rec_p.add_argument("--details", default=None, help="JSON string of extra details")
    rec_p.add_argument("--audit-file", dest="audit_file", default=None)
    rec_p.set_defaults(func=cmd_audit_record)

    # clear
    clr_p = audit_sub.add_parser("clear", help="Clear all audit events")
    clr_p.add_argument("--audit-file", dest="audit_file", default=None)
    clr_p.set_defaults(func=cmd_audit_clear)
