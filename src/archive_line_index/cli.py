"""Importable single-target adapter over independent indexing/persistence APIs."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from .api import build_line_index
from .persistence.raw import write_raw_index
from .persistence.sqlite import write_sqlite_index


class _ParserExit(Exception):
    def __init__(self, status: int, message: str | None) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class _Parser(argparse.ArgumentParser):
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        raise _ParserExit(status, message)


def _parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="archive-line-index",
        description="Index one target into SQLite and raw offsets.",
    )
    parser.add_argument("target", metavar="TARGET")
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT_STEM",
        help="shared output path stem; extensions are appended",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace distinct existing output files",
    )
    return parser


def _preflight(target: Path, outputs: tuple[Path, Path], *, overwrite: bool) -> None:
    source_name = os.path.normcase(os.path.abspath(target))
    for output in outputs:
        if os.path.normcase(os.path.abspath(output)) == source_name:
            raise ValueError(
                f"Output names the source: {output}; select a distinct output stem"
            )
        try:
            same = os.path.samefile(target, output)
        except FileNotFoundError:
            same = False
        if same:
            raise ValueError(f"Output aliases the source: {output}")
        if not overwrite and os.path.lexists(output):
            raise FileExistsError(f"Protected destination exists: {output}")


def main(argv: Sequence[str] | None = None) -> int:
    """Index one filesystem target once and write SQLite then raw from one array.

    Args:
        argv: Explicit argument sequence, or None for sys.argv[1:]. A command-line
            string, bytes, nonsequence or nonstring element raises TypeError.

    Help and usage errors return integer statuses without exiting the caller.
    Importing this module performs no parsing, path inspection or CLI execution.
    """
    if argv is not None and (
        isinstance(argv, (str, bytes))
        or not isinstance(argv, Sequence)
        or any(not isinstance(value, str) for value in argv)
    ):
        raise TypeError("argv must be a sequence of strings or None")
    values = list(sys.argv[1:] if argv is None else argv)
    try:
        options = _parser().parse_args(values)
    except _ParserExit as outcome:
        if outcome.message:
            print(outcome.message, file=sys.stderr, end="")
        return outcome.status
    target = Path(options.target)
    stem = (
        Path(options.output)
        if options.output is not None
        else target.parent / target.stem
    )
    sqlite = Path(str(stem) + ".sqlite3")
    raw = Path(str(stem) + ".u64")
    try:
        _preflight(target, (sqlite, raw), overwrite=options.overwrite)
    except (OSError, ValueError) as error:
        print(f"Indexing failed: {error}", file=sys.stderr)
        return 1
    offsets = build_line_index(target)
    write_sqlite_index(offsets, sqlite, overwrite=options.overwrite)
    write_raw_index(offsets, raw, overwrite=options.overwrite)
    print(f"Indexed {len(offsets) - 1} lines: {sqlite}; {raw}")
    return 0
