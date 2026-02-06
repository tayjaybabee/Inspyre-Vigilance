from __future__ import annotations

import argparse

from inspyre_vigilance.core.vigilance_core import main as run_core

from .version import print_version_info


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspyre-vigilance",
        description="Inspyre Vigilance system intelligence runner.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Show version information.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        return print_version_info()

    exit_code = run_core()
    if isinstance(exit_code, int):
        return exit_code
    return 0
