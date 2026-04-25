"""Tests for stacksnap.cli_schedule module."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from stacksnap.cli_schedule import (
    cmd_schedule_add,
    cmd_schedule_remove,
    cmd_schedule_list,
    cmd_schedule_run,
    build_schedule_parser,
)


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


@pytest.fixture
def sched_file(tmp_path):
    return tmp_path / "schedules.json"


def test_cmd_schedule_add_prints_confirmation(capsys, tmp_path):
    sf = tmp_path / "s.json"
    with patch("stacksnap.cli_schedule.add_schedule") as mock_add:
        mock_add.return_value = {
            "project": "myapp",
            "interval_minutes": 30,
            "label_prefix": "auto",
        }
        cmd_schedule_add(_ns(project="myapp", interval=30, prefix="auto"))
    out = capsys.readouterr().out
    assert "myapp" in out
    assert "30" in out


def test_cmd_schedule_remove_success(capsys):
    with patch("stacksnap.cli_schedule.remove_schedule", return_value=True):
        cmd_schedule_remove(_ns(project="myapp"))
    assert "Removed" in capsys.readouterr().out


def test_cmd_schedule_remove_missing(capsys):
    with patch("stacksnap.cli_schedule.remove_schedule", return_value=False):
        with pytest.raises(SystemExit):
            cmd_schedule_remove(_ns(project="ghost"))


def test_cmd_schedule_list_empty(capsys):
    with patch("stacksnap.cli_schedule.list_schedules", return_value=[]):
        cmd_schedule_list(_ns())
    assert "No schedules" in capsys.readouterr().out


def test_cmd_schedule_list_shows_entries(capsys):
    entries = [
        {"project": "proj", "interval_minutes": 15, "last_run": None, "label_prefix": "auto"}
    ]
    with patch("stacksnap.cli_schedule.list_schedules", return_value=entries):
        cmd_schedule_list(_ns())
    out = capsys.readouterr().out
    assert "proj" in out
    assert "15" in out


def test_cmd_schedule_run_not_due(capsys):
    with patch("stacksnap.cli_schedule.is_due", return_value=False):
        cmd_schedule_run(_ns(project="proj"))
    assert "not due" in capsys.readouterr().out


def test_cmd_schedule_run_when_due(capsys):
    entry = {"project": "proj", "interval_minutes": 5, "label_prefix": "auto"}
    snap = {"label": "auto-proj", "python": "3.11.0"}
    with patch("stacksnap.cli_schedule.is_due", return_value=True), \
         patch("stacksnap.cli_schedule.get_schedule", return_value=entry), \
         patch("stacksnap.cli_schedule.capture_snapshot", return_value=snap), \
         patch("stacksnap.cli_schedule.save_snapshot", return_value="/tmp/snap.json"), \
         patch("stacksnap.schedule.mark_ran"):
        cmd_schedule_run(_ns(project="proj"))
    assert "saved" in capsys.readouterr().out


def test_build_schedule_parser_returns_parser():
    parser = build_schedule_parser()
    assert parser is not None
