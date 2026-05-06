"""Registers the bookmark sub-command into the main stacksnap CLI parser."""

from __future__ import annotations

import argparse
from typing import Optional

from stacksnap.cli_bookmark import build_bookmark_parser


class _BookmarkProxy:
    """Thin proxy so the integration module can be called from tests."""

    def __init__(self, snapshot_dir: Optional[str] = None) -> None:
        self._snapshot_dir = snapshot_dir

    def dispatch(self, argv: list[str]) -> None:
        parser = build_standalone_parser()
        args = parser.parse_args(argv)
        if self._snapshot_dir:
            args.snapshot_dir = self._snapshot_dir
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()


def build_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone parser for the bookmark command group."""
    parser = argparse.ArgumentParser(
        prog="stacksnap bookmark",
        description="Manage snapshot bookmarks",
    )
    sub = parser.add_subparsers(dest="bookmark_cmd")
    build_bookmark_parser(sub)  # type: ignore[arg-type]
    return parser


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Hook called by the main CLI to register the bookmark command."""
    build_bookmark_parser(subparsers)


def dispatch(args: argparse.Namespace) -> None:
    """Dispatch an already-parsed Namespace to the correct bookmark handler."""
    if hasattr(args, "func"):
        args.func(args)
