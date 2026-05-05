"""Tests for stacksnap.audit and stacksnap.cli_audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from stacksnap.audit import clear_events, get_events, record_event
from stacksnap.cli_audit import cmd_audit_clear, cmd_audit_log, cmd_audit_record


@pytest.fixture()
def audit_file(tmp_path: Path) -> str:
    return str(tmp_path / "audit.jsonl")


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


# --- record_event ---

def test_record_event_returns_entry(audit_file):
    entry = record_event("capture", "snap-001", audit_file=audit_file)
    assert entry["action"] == "capture"
    assert entry["snapshot_id"] == "snap-001"
    assert "timestamp" in entry


def test_record_event_persists(audit_file):
    record_event("restore", "snap-002", audit_file=audit_file)
    events = get_events(audit_file=audit_file)
    assert len(events) == 1
    assert events[0]["action"] == "restore"


def test_record_event_appends_multiple(audit_file):
    record_event("capture", "snap-001", audit_file=audit_file)
    record_event("restore", "snap-001", audit_file=audit_file)
    events = get_events(audit_file=audit_file)
    assert len(events) == 2


def test_record_event_stores_details(audit_file):
    record_event("archive", "snap-003", details={"reason": "old"}, audit_file=audit_file)
    events = get_events(audit_file=audit_file)
    assert events[0]["details"]["reason"] == "old"


def test_record_event_empty_action_raises(audit_file):
    with pytest.raises(ValueError, match="action"):
        record_event("", "snap-001", audit_file=audit_file)


def test_record_event_empty_snapshot_id_raises(audit_file):
    with pytest.raises(ValueError, match="snapshot_id"):
        record_event("capture", "", audit_file=audit_file)


# --- get_events ---

def test_get_events_filter_by_snapshot_id(audit_file):
    record_event("capture", "snap-A", audit_file=audit_file)
    record_event("capture", "snap-B", audit_file=audit_file)
    events = get_events(snapshot_id="snap-A", audit_file=audit_file)
    assert all(e["snapshot_id"] == "snap-A" for e in events)
    assert len(events) == 1


def test_get_events_filter_by_action(audit_file):
    record_event("capture", "snap-A", audit_file=audit_file)
    record_event("restore", "snap-A", audit_file=audit_file)
    events = get_events(action="restore", audit_file=audit_file)
    assert len(events) == 1
    assert events[0]["action"] == "restore"


def test_get_events_no_file_returns_empty(audit_file):
    events = get_events(audit_file=audit_file)
    assert events == []


# --- clear_events ---

def test_clear_events_returns_count(audit_file):
    record_event("capture", "snap-001", audit_file=audit_file)
    record_event("restore", "snap-001", audit_file=audit_file)
    removed = clear_events(audit_file=audit_file)
    assert removed == 2


def test_clear_events_removes_all(audit_file):
    record_event("capture", "snap-001", audit_file=audit_file)
    clear_events(audit_file=audit_file)
    assert get_events(audit_file=audit_file) == []


def test_clear_events_no_file_returns_zero(audit_file):
    assert clear_events(audit_file=audit_file) == 0


# --- CLI ---

def test_cmd_audit_log_prints_events(audit_file, capsys):
    record_event("capture", "snap-X", audit_file=audit_file)
    cmd_audit_log(_ns(snapshot_id=None, action=None, audit_file=audit_file))
    out = capsys.readouterr().out
    assert "snap-X" in out


def test_cmd_audit_log_no_events_message(audit_file, capsys):
    cmd_audit_log(_ns(snapshot_id=None, action=None, audit_file=audit_file))
    out = capsys.readouterr().out
    assert "No audit events" in out


def test_cmd_audit_record_prints_confirmation(audit_file, capsys):
    cmd_audit_record(_ns(action="capture", snapshot_id="snap-Y", details=None, audit_file=audit_file))
    out = capsys.readouterr().out
    assert "capture" in out and "snap-Y" in out


def test_cmd_audit_clear_prints_count(audit_file, capsys):
    record_event("capture", "snap-Z", audit_file=audit_file)
    cmd_audit_clear(_ns(audit_file=audit_file))
    out = capsys.readouterr().out
    assert "1" in out
