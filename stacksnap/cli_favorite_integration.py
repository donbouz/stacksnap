"""Integration shim that wires the favorite sub-commands into the main CLI."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from stacksnap.cli_favorite import (
    build_favorite_parser,
    cmd_favorite_add,
    cmd_favorite_remove,
    cmd_favorite_list,
    cmd_favorite_check,
)


class _FavoriteProxy:
    """Proxy object that exposes favorite commands as methods."""

    def __init__(self, snapshot_dir: Optional[Path] = None) -> None:
        self._dir = snapshot_dir or Path.home() / ".stacksnap" / "snapshots"

    def _ns(self, **kwargs: object) -> argparse.Namespace:
        return argparse.Namespace(snapshot_dir=str(self._dir), **kwargs)

    def add(self, snapshot_id: str) -> None:
        cmd_favorite_add(self._ns(snapshot_id=snapshot_id))

    def remove(self, snapshot_id: str) -> None:
        cmd_favorite_remove(self._ns(snapshot_id=snapshot_id))

    def list(self) -> None:  # noqa: A003
        cmd_favorite_list(self._ns())

    def check(self, snapshot_id: str) -> None:
        cmd_favorite_check(self._ns(snapshot_id=snapshot_id))


def dispatch(args: argparse.Namespace) -> None:
    """Route parsed args to the correct favorite command handler."""
    handler = getattr(args, "func", None)
    if handler is None:
        raise SystemExit("No favorite sub-command specified.")
    handler(args)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register favorite commands with an existing top-level subparser."""
    build_favorite_parser(subparsers)


def build_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone parser for the favorite command group."""
    parser = argparse.ArgumentParser(prog="stacksnap-favorite")
    sub = parser.add_subparsers(dest="favorite_cmd", required=True)
    build_favorite_parser(sub)
    return parser
