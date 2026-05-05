"""Integration helper: wire watchlist commands into the main CLI parser.

This module is imported by the top-level CLI entry-point to register the
``watch`` sub-command group alongside the existing command groups.
"""

from __future__ import annotations

import argparse

from stacksnap.cli_watchlist import build_watchlist_parser


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register watchlist sub-commands with *subparsers*.

    Usage in main CLI::

        from stacksnap.cli_watchlist_integration import register
        register(main_subparsers)
    """
    build_watchlist_parser(subparsers)


def dispatch(args: argparse.Namespace) -> bool:
    """Dispatch a parsed namespace to the correct watchlist handler.

    Returns True if the command was handled, False otherwise.
    This allows the main CLI to fall through to other dispatchers.
    """
    if not hasattr(args, "watch_cmd"):
        return False
    if not hasattr(args, "func"):
        return False
    args.func(args)
    return True


def build_standalone_parser() -> argparse.ArgumentParser:
    """Build a standalone argument parser for the watchlist sub-system.

    Useful for testing or running watchlist commands in isolation::

        python -m stacksnap.cli_watchlist_integration watch add snap-001
    """
    parser = argparse.ArgumentParser(
        prog="stacksnap-watch",
        description="Manage the StackSnap snapshot watchlist.",
    )
    subparsers = parser.add_subparsers(dest="watch_cmd", required=True)
    build_watchlist_parser(
        # build_watchlist_parser expects a top-level subparsers object;
        # wrap it so the nested sub-commands are registered correctly.
        type(
            "_FakeSubparsers",
            (),
            {
                "add_parser": lambda self, name, **kw: (
                    _WatchProxy(subparsers, name, **kw)
                )
            },
        )()
    )
    return parser


class _WatchProxy:
    """Thin proxy that forwards add_subparsers / set_defaults to the real parser."""

    def __init__(self, subparsers: argparse._SubParsersAction, name: str, **kw):
        self._parser = subparsers.add_parser(name, **kw)

    def __getattr__(self, item):
        return getattr(self._parser, item)

    def add_subparsers(self, **kw):
        return self._parser.add_subparsers(**kw)
