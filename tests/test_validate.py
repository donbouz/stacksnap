"""Tests for stacksnap.validate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stacksnap.validate import (
    is_valid,
    validate_snapshot,
    validate_snapshot_file,
)


@pytest.fixture()
def valid_snapshot() -> dict:
    return {
        "label": "my-snap",
        "timestamp": "2024-01-01T00:00:00",
        "python": {"version": "3.11.4", "packages": {"requests": "2.31.0"}},
        "node": {"version": "20.3.0", "packages": {"react": "18.2.0"}},
        "env": {"NODE_ENV": "development"},
    }


def test_valid_snapshot_returns_no_errors(valid_snapshot):
    assert validate_snapshot(valid_snapshot) == []


def test_is_valid_returns_true_for_good_snapshot(valid_snapshot):
    assert is_valid(valid_snapshot) is True


def test_missing_top_level_key_reported(valid_snapshot):
    del valid_snapshot["label"]
    errors = validate_snapshot(valid_snapshot)
    assert any("label" in e for e in errors)


def test_multiple_missing_keys_all_reported():
    errors = validate_snapshot({})
    missing = {"label", "timestamp", "python", "node", "env"}
    for key in missing:
        assert any(key in e for e in errors), f"Expected error for missing key '{key}'"


def test_non_dict_snapshot_returns_type_error():
    errors = validate_snapshot(["not", "a", "dict"])
    assert len(errors) == 1
    assert "mapping" in errors[0]


def test_python_section_missing_version(valid_snapshot):
    del valid_snapshot["python"]["version"]
    errors = validate_snapshot(valid_snapshot)
    assert any("python" in e and "version" in e for e in errors)


def test_python_section_not_dict(valid_snapshot):
    valid_snapshot["python"] = "3.11"
    errors = validate_snapshot(valid_snapshot)
    assert any("python" in e and "mapping" in e for e in errors)


def test_node_section_missing_packages(valid_snapshot):
    del valid_snapshot["node"]["packages"]
    errors = validate_snapshot(valid_snapshot)
    assert any("node" in e and "packages" in e for e in errors)


def test_env_not_dict_reported(valid_snapshot):
    valid_snapshot["env"] = "NOT_A_DICT"
    errors = validate_snapshot(valid_snapshot)
    assert any("env" in e and "mapping" in e for e in errors)


def test_validate_snapshot_file_not_found(tmp_path):
    errors = validate_snapshot_file(tmp_path / "missing.json")
    assert any("not found" in e.lower() for e in errors)


def test_validate_snapshot_file_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    errors = validate_snapshot_file(bad_file)
    assert any("Invalid JSON" in e for e in errors)


def test_validate_snapshot_file_valid(tmp_path, valid_snapshot):
    snap_file = tmp_path / "snap.json"
    snap_file.write_text(json.dumps(valid_snapshot))
    errors = validate_snapshot_file(snap_file)
    assert errors == []


def test_is_valid_returns_false_for_bad_snapshot():
    assert is_valid({}) is False
