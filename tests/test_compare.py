"""Tests for stacksnap.compare."""

from __future__ import annotations

import pytest

from stacksnap.compare import compare_snapshots, format_compare, _score_section


@pytest.fixture()
def snap_a():
    return {
        "label": "snap-alpha",
        "python": {"version": "3.11.4", "packages": {"requests": "2.31.0"}},
        "node": {"version": "20.3.0", "packages": {"lodash": "4.17.21"}},
        "env_vars": {"DEBUG": "1", "APP_ENV": "dev"},
        "git": {"branch": "main", "commit": "abc123"},
    }


@pytest.fixture()
def snap_b():
    return {
        "label": "snap-beta",
        "python": {"version": "3.11.4", "packages": {"requests": "2.31.0"}},
        "node": {"version": "18.0.0", "packages": {"lodash": "4.17.21"}},
        "env_vars": {"DEBUG": "0", "APP_ENV": "dev"},
        "git": {"branch": "feature/x", "commit": "def456"},
    }


def test_score_section_identical_dicts():
    assert _score_section({"a": 1}, {"a": 1}) == 1.0


def test_score_section_completely_different_dicts():
    assert _score_section({"a": 1}, {"b": 2}) == 0.0


def test_score_section_partial_match():
    score = _score_section({"a": 1, "b": 2}, {"a": 1, "b": 99})
    assert score == pytest.approx(0.5)


def test_score_section_both_none():
    assert _score_section(None, None) == 1.0


def test_score_section_one_none():
    assert _score_section({"a": 1}, None) == 0.0


def test_score_section_scalar_match():
    assert _score_section("3.11", "3.11") == 1.0


def test_score_section_scalar_mismatch():
    assert _score_section("3.11", "3.10") == 0.0


def test_compare_snapshots_returns_required_keys(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    assert "score" in report
    assert "breakdown" in report
    assert "labels" in report


def test_compare_snapshots_labels(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    assert report["labels"] == ["snap-alpha", "snap-beta"]


def test_compare_snapshots_score_range(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    assert 0.0 <= report["score"] <= 1.0


def test_compare_identical_snapshots(snap_a):
    report = compare_snapshots(snap_a, snap_a)
    assert report["score"] == pytest.approx(1.0)


def test_compare_breakdown_has_all_sections(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    for section in ("python", "node", "env_vars", "git"):
        assert section in report["breakdown"]


def test_format_compare_contains_labels(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    output = format_compare(report)
    assert "snap-alpha" in output
    assert "snap-beta" in output


def test_format_compare_contains_percentage(snap_a, snap_b):
    report = compare_snapshots(snap_a, snap_b)
    output = format_compare(report)
    assert "%" in output
