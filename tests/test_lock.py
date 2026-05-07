"""Tests for stacksnap.lock."""

from __future__ import annotations

import pytest

from stacksnap.lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    get_locked,
    clear_locks,
)


@pytest.fixture()
def lock_dir(tmp_path):
    return str(tmp_path)


def test_lock_snapshot_returns_true_when_new(lock_dir):
    assert lock_snapshot("snap-001", lock_dir) is True


def test_lock_snapshot_returns_false_when_duplicate(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    assert lock_snapshot("snap-001", lock_dir) is False


def test_lock_snapshot_persists(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    assert is_locked("snap-001", lock_dir) is True


def test_lock_multiple_snapshots(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    lock_snapshot("snap-002", lock_dir)
    locked = get_locked(lock_dir)
    assert "snap-001" in locked
    assert "snap-002" in locked


def test_unlock_returns_true_when_present(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    assert unlock_snapshot("snap-001", lock_dir) is True


def test_unlock_returns_false_when_absent(lock_dir):
    assert unlock_snapshot("snap-999", lock_dir) is False


def test_unlock_removes_entry(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    unlock_snapshot("snap-001", lock_dir)
    assert is_locked("snap-001", lock_dir) is False


def test_is_locked_false_for_unknown(lock_dir):
    assert is_locked("no-such-snap", lock_dir) is False


def test_get_locked_empty_when_none(lock_dir):
    assert get_locked(lock_dir) == []


def test_clear_locks_returns_count(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    lock_snapshot("snap-002", lock_dir)
    assert clear_locks(lock_dir) == 2


def test_clear_locks_removes_all(lock_dir):
    lock_snapshot("snap-001", lock_dir)
    clear_locks(lock_dir)
    assert get_locked(lock_dir) == []


def test_lock_empty_id_raises(lock_dir):
    with pytest.raises(ValueError):
        lock_snapshot("", lock_dir)
