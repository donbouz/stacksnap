"""Tests for stacksnap/tags.py"""

import json
import pytest
from pathlib import Path

from stacksnap.tags import (
    add_tag,
    remove_tag,
    get_tags,
    find_by_tag,
    list_all_tags,
    rename_snapshot_tags,
    purge_snapshot_tags,
    TAGS_FILE,
)


@pytest.fixture
def tag_dir(tmp_path):
    return tmp_path


def test_add_tag_creates_entry(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    assert "stable" in get_tags(tag_dir, "snap-1")


def test_add_tag_no_duplicates(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    add_tag(tag_dir, "snap-1", "stable")
    assert get_tags(tag_dir, "snap-1").count("stable") == 1


def test_add_multiple_tags(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    add_tag(tag_dir, "snap-1", "prod")
    tags = get_tags(tag_dir, "snap-1")
    assert "stable" in tags
    assert "prod" in tags


def test_remove_tag_returns_true_when_present(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    result = remove_tag(tag_dir, "snap-1", "stable")
    assert result is True
    assert "stable" not in get_tags(tag_dir, "snap-1")


def test_remove_tag_returns_false_when_absent(tag_dir):
    result = remove_tag(tag_dir, "snap-1", "nonexistent")
    assert result is False


def test_get_tags_returns_empty_list_for_unknown_snapshot(tag_dir):
    assert get_tags(tag_dir, "ghost") == []


def test_find_by_tag_returns_matching_snapshots(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    add_tag(tag_dir, "snap-2", "stable")
    add_tag(tag_dir, "snap-3", "dev")
    result = find_by_tag(tag_dir, "stable")
    assert "snap-1" in result
    assert "snap-2" in result
    assert "snap-3" not in result


def test_find_by_tag_returns_empty_when_none_match(tag_dir):
    add_tag(tag_dir, "snap-1", "dev")
    assert find_by_tag(tag_dir, "stable") == []


def test_list_all_tags_returns_full_index(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    add_tag(tag_dir, "snap-2", "dev")
    index = list_all_tags(tag_dir)
    assert "snap-1" in index
    assert "snap-2" in index


def test_rename_snapshot_tags_migrates_entries(tag_dir):
    add_tag(tag_dir, "old-snap", "stable")
    rename_snapshot_tags(tag_dir, "old-snap", "new-snap")
    assert get_tags(tag_dir, "new-snap") == ["stable"]
    assert get_tags(tag_dir, "old-snap") == []


def test_purge_snapshot_tags_removes_entry(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    purge_snapshot_tags(tag_dir, "snap-1")
    assert get_tags(tag_dir, "snap-1") == []
    index = list_all_tags(tag_dir)
    assert "snap-1" not in index


def test_tags_file_is_valid_json(tag_dir):
    add_tag(tag_dir, "snap-1", "stable")
    raw = (tag_dir / TAGS_FILE).read_text()
    data = json.loads(raw)
    assert isinstance(data, dict)
