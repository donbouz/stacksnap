"""Tests for stacksnap.template"""

from __future__ import annotations

import pytest
from pathlib import Path

from stacksnap.template import (
    save_template,
    load_template,
    list_templates,
    delete_template,
    instantiate_template,
)


@pytest.fixture()
def tdir(tmp_path: Path) -> Path:
    return tmp_path / "templates"


_SNAP = {
    "label": "my-snap",
    "python": {"version": "3.11.2"},
    "node": {"version": "20.0.0"},
    "env": {"DEBUG": "1"},
}


def test_save_template_returns_true_when_new(tdir):
    assert save_template("base", _SNAP, tdir) is True


def test_save_template_returns_false_on_overwrite(tdir):
    save_template("base", _SNAP, tdir)
    assert save_template("base", _SNAP, tdir) is False


def test_save_template_persists(tdir):
    save_template("base", _SNAP, tdir)
    loaded = load_template("base", tdir)
    assert loaded["label"] == "my-snap"
    assert loaded["_template_name"] == "base"


def test_save_template_empty_name_raises(tdir):
    with pytest.raises(ValueError):
        save_template("", _SNAP, tdir)


def test_load_template_missing_raises(tdir):
    with pytest.raises(FileNotFoundError):
        load_template("ghost", tdir)


def test_list_templates_empty_dir(tdir):
    assert list_templates(tdir) == []


def test_list_templates_returns_sorted_names(tdir):
    save_template("zebra", _SNAP, tdir)
    save_template("alpha", _SNAP, tdir)
    save_template("mango", _SNAP, tdir)
    assert list_templates(tdir) == ["alpha", "mango", "zebra"]


def test_delete_template_returns_true(tdir):
    save_template("base", _SNAP, tdir)
    assert delete_template("base", tdir) is True


def test_delete_template_returns_false_when_missing(tdir):
    assert delete_template("ghost", tdir) is False


def test_delete_template_removes_from_list(tdir):
    save_template("base", _SNAP, tdir)
    delete_template("base", tdir)
    assert "base" not in list_templates(tdir)


def test_instantiate_template_strips_metadata(tdir):
    save_template("base", _SNAP, tdir)
    snap = instantiate_template("base", template_dir=tdir)
    assert "_template_name" not in snap


def test_instantiate_template_applies_overrides(tdir):
    save_template("base", _SNAP, tdir)
    snap = instantiate_template("base", overrides={"python": {"version": "3.12.0"}}, template_dir=tdir)
    assert snap["python"]["version"] == "3.12.0"


def test_instantiate_template_does_not_mutate_original(tdir):
    save_template("base", _SNAP, tdir)
    instantiate_template("base", overrides={"env": {"DEBUG": "0"}}, template_dir=tdir)
    reloaded = load_template("base", tdir)
    assert reloaded["env"]["DEBUG"] == "1"
