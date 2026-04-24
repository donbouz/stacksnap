"""Tests for stacksnap.restore module."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from stacksnap.restore import (
    restore_env_vars,
    restore_python,
    restore_node,
    restore_snapshot,
)


SAMPLE_SNAPSHOT = {
    "label": "test-snap",
    "timestamp": "2024-01-01T00:00:00",
    "python_packages": ["requests==2.31.0", "click==8.1.7"],
    "node_packages": ["typescript@5.0.0"],
    "env_vars": {"DEBUG": "1", "APP_ENV": "development"},
}


@pytest.fixture
def snapshot_dir(tmp_path):
    snap_file = tmp_path / "test-snap.json"
    snap_file.write_text(json.dumps(SAMPLE_SNAPSHOT))
    return str(tmp_path)


def test_restore_env_vars_returns_dict():
    result = restore_env_vars(SAMPLE_SNAPSHOT)
    assert result == {"DEBUG": "1", "APP_ENV": "development"}


def test_restore_env_vars_missing_key():
    result = restore_env_vars({"label": "x"})
    assert result == {}


@patch("stacksnap.restore._run_silent", return_value=(0, ""))
def test_restore_python_success(mock_run):
    warnings = restore_python(SAMPLE_SNAPSHOT)
    assert warnings == []
    assert mock_run.call_count == 2


@patch("stacksnap.restore._run_silent", return_value=(1, "error: not found"))
def test_restore_python_records_warning_on_failure(mock_run):
    warnings = restore_python(SAMPLE_SNAPSHOT)
    assert len(warnings) == 2
    assert all("pip" in w for w in warnings)


@patch("stacksnap.restore._run_silent", return_value=(0, ""))
def test_restore_python_skips_when_no_packages(mock_run):
    warnings = restore_python({"python_packages": []})
    assert warnings == []
    mock_run.assert_not_called()


@patch("stacksnap.restore._run_silent", return_value=(0, ""))
def test_restore_node_success(mock_run):
    warnings = restore_node(SAMPLE_SNAPSHOT)
    assert warnings == []
    assert mock_run.call_count == 1


@patch("stacksnap.restore._run_silent", return_value=(1, "npm ERR!"))
def test_restore_node_records_warning_on_failure(mock_run):
    warnings = restore_node(SAMPLE_SNAPSHOT)
    assert len(warnings) == 1
    assert "npm" in warnings[0]


@patch("stacksnap.restore.restore_node", return_value=[])
@patch("stacksnap.restore.restore_python", return_value=[])
def test_restore_snapshot_returns_expected_keys(mock_py, mock_node, snapshot_dir):
    result = restore_snapshot("test-snap", snapshots_dir=snapshot_dir)
    assert result["label"] == "test-snap"
    assert "warnings" in result
    assert "env_vars" in result


@patch("stacksnap.restore.restore_node", return_value=["npm: failed"])
@patch("stacksnap.restore.restore_python", return_value=["pip: failed"])
def test_restore_snapshot_aggregates_warnings(mock_py, mock_node, snapshot_dir):
    result = restore_snapshot("test-snap", snapshots_dir=snapshot_dir)
    assert len(result["warnings"]) == 2


@patch("stacksnap.restore.restore_node")
@patch("stacksnap.restore.restore_python")
def test_restore_snapshot_skips_python_when_disabled(mock_py, mock_node, snapshot_dir):
    restore_snapshot("test-snap", snapshots_dir=snapshot_dir, restore_python_pkgs=False)
    mock_py.assert_not_called()
    mock_node.assert_called_once()


def test_restore_snapshot_raises_for_missing_label(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_snapshot("nonexistent", snapshots_dir=str(tmp_path))
