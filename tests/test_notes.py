"""Tests for stacksnap.notes."""

from __future__ import annotations

import pytest
from pathlib import Path

from stacksnap.notes import add_note, get_notes, delete_notes, format_notes


@pytest.fixture()
def note_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_add_note_returns_entry(note_dir):
    entry = add_note("snap-1", "hello world", note_dir)
    assert entry["text"] == "hello world"
    assert "timestamp" in entry


def test_add_note_persists(note_dir):
    add_note("snap-1", "first note", note_dir)
    notes = get_notes("snap-1", note_dir)
    assert len(notes) == 1
    assert notes[0]["text"] == "first note"


def test_add_multiple_notes_ordered(note_dir):
    add_note("snap-1", "alpha", note_dir)
    add_note("snap-1", "beta", note_dir)
    notes = get_notes("snap-1", note_dir)
    assert [n["text"] for n in notes] == ["alpha", "beta"]


def test_add_note_strips_whitespace(note_dir):
    entry = add_note("snap-1", "  trimmed  ", note_dir)
    assert entry["text"] == "trimmed"


def test_add_note_empty_text_raises(note_dir):
    with pytest.raises(ValueError, match="empty"):
        add_note("snap-1", "   ", note_dir)


def test_get_notes_empty_when_missing(note_dir):
    assert get_notes("nonexistent", note_dir) == []


def test_notes_isolated_per_snapshot(note_dir):
    add_note("snap-1", "for snap1", note_dir)
    add_note("snap-2", "for snap2", note_dir)
    assert len(get_notes("snap-1", note_dir)) == 1
    assert get_notes("snap-1", note_dir)[0]["text"] == "for snap1"


def test_delete_notes_returns_true_when_present(note_dir):
    add_note("snap-1", "bye", note_dir)
    assert delete_notes("snap-1", note_dir) is True


def test_delete_notes_removes_entries(note_dir):
    add_note("snap-1", "bye", note_dir)
    delete_notes("snap-1", note_dir)
    assert get_notes("snap-1", note_dir) == []


def test_delete_notes_returns_false_when_absent(note_dir):
    assert delete_notes("snap-missing", note_dir) is False


def test_format_notes_no_entries(note_dir):
    result = format_notes("snap-1", [])
    assert "No notes" in result


def test_format_notes_shows_text(note_dir):
    entries = [{"text": "important", "timestamp": "2024-01-01T00:00:00+00:00"}]
    result = format_notes("snap-1", entries)
    assert "important" in result
    assert "snap-1" in result
