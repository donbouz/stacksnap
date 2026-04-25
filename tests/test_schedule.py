"""Tests for stacksnap.schedule module."""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from stacksnap.schedule import (
    add_schedule,
    remove_schedule,
    get_schedule,
    list_schedules,
    is_due,
    mark_ran,
)


@pytest.fixture
def sched_file(tmp_path):
    return tmp_path / "schedules.json"


def test_add_schedule_creates_entry(sched_file):
    entry = add_schedule("myproject", 30, schedule_file=sched_file)
    assert entry["project"] == "myproject"
    assert entry["interval_minutes"] == 30
    assert entry["last_run"] is None


def test_add_schedule_persists(sched_file):
    add_schedule("proj", 60, schedule_file=sched_file)
    data = json.loads(sched_file.read_text())
    assert "proj" in data


def test_add_schedule_invalid_interval(sched_file):
    with pytest.raises(ValueError):
        add_schedule("proj", 0, schedule_file=sched_file)


def test_remove_schedule_returns_true(sched_file):
    add_schedule("proj", 10, schedule_file=sched_file)
    assert remove_schedule("proj", schedule_file=sched_file) is True


def test_remove_schedule_returns_false_when_missing(sched_file):
    assert remove_schedule("nope", schedule_file=sched_file) is False


def test_get_schedule_returns_entry(sched_file):
    add_schedule("alpha", 15, schedule_file=sched_file)
    entry = get_schedule("alpha", schedule_file=sched_file)
    assert entry is not None
    assert entry["interval_minutes"] == 15


def test_get_schedule_returns_none_for_missing(sched_file):
    assert get_schedule("ghost", schedule_file=sched_file) is None


def test_list_schedules_returns_all(sched_file):
    add_schedule("a", 5, schedule_file=sched_file)
    add_schedule("b", 10, schedule_file=sched_file)
    result = list_schedules(schedule_file=sched_file)
    assert len(result) == 2


def test_is_due_when_never_run(sched_file):
    add_schedule("fresh", 60, schedule_file=sched_file)
    assert is_due("fresh", schedule_file=sched_file) is True


def test_is_due_not_yet_elapsed(sched_file):
    add_schedule("recent", 60, schedule_file=sched_file)
    mark_ran("recent", schedule_file=sched_file)
    assert is_due("recent", schedule_file=sched_file) is False


def test_is_due_after_elapsed(sched_file):
    add_schedule("old", 1, schedule_file=sched_file)
    data = json.loads(sched_file.read_text())
    past = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    data["old"]["last_run"] = past
    sched_file.write_text(json.dumps(data))
    assert is_due("old", schedule_file=sched_file) is True


def test_mark_ran_updates_timestamp(sched_file):
    add_schedule("proj", 30, schedule_file=sched_file)
    mark_ran("proj", schedule_file=sched_file)
    entry = get_schedule("proj", schedule_file=sched_file)
    assert entry["last_run"] is not None
