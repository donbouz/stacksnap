"""Tests for stacksnap.alias."""

import pytest
from pathlib import Path

from stacksnap.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)


@pytest.fixture()
def alias_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_set_alias_returns_true_when_new(alias_dir):
    assert set_alias(alias_dir, "prod", "snap-001") is True


def test_set_alias_returns_false_when_overwrite(alias_dir):
    set_alias(alias_dir, "prod", "snap-001")
    assert set_alias(alias_dir, "prod", "snap-002") is False


def test_set_alias_persists(alias_dir):
    set_alias(alias_dir, "staging", "snap-010")
    assert resolve_alias(alias_dir, "staging") == "snap-010"


def test_set_alias_overwrites_value(alias_dir):
    set_alias(alias_dir, "prod", "snap-001")
    set_alias(alias_dir, "prod", "snap-999")
    assert resolve_alias(alias_dir, "prod") == "snap-999"


def test_set_alias_empty_raises(alias_dir):
    with pytest.raises(ValueError):
        set_alias(alias_dir, "", "snap-001")


def test_set_alias_whitespace_raises(alias_dir):
    with pytest.raises(ValueError):
        set_alias(alias_dir, "   ", "snap-001")


def test_remove_alias_returns_true_when_present(alias_dir):
    set_alias(alias_dir, "dev", "snap-002")
    assert remove_alias(alias_dir, "dev") is True


def test_remove_alias_returns_false_when_missing(alias_dir):
    assert remove_alias(alias_dir, "ghost") is False


def test_remove_alias_deletes_entry(alias_dir):
    set_alias(alias_dir, "dev", "snap-002")
    remove_alias(alias_dir, "dev")
    assert resolve_alias(alias_dir, "dev") is None


def test_resolve_alias_returns_none_for_unknown(alias_dir):
    assert resolve_alias(alias_dir, "nope") is None


def test_list_aliases_empty(alias_dir):
    assert list_aliases(alias_dir) == []


def test_list_aliases_returns_all(alias_dir):
    set_alias(alias_dir, "a", "snap-001")
    set_alias(alias_dir, "b", "snap-002")
    result = list_aliases(alias_dir)
    names = [e["alias"] for e in result]
    assert "a" in names and "b" in names


def test_list_aliases_sorted(alias_dir):
    set_alias(alias_dir, "z", "snap-z")
    set_alias(alias_dir, "a", "snap-a")
    result = list_aliases(alias_dir)
    assert result[0]["alias"] == "a"
