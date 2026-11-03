"""Importable single-target adapter over independent indexing/persistence APIs."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from .api import build_line_index
from .errors import ArchiveLineIndexError
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


def _diagnostic(title: str, error: BaseException, published: list[Path]) -> None:
    print(f"{title}: {error}" if str(error) else title, file=sys.stderr)
    for note in getattr(error, "__notes__", ()):
        print(note, file=sys.stderr)
    for path in published:
        print(f"Already published: {path}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    """Index one filesystem target once and write SQLite then raw from one array.

    Args:
        argv: Explicit argument sequence, or None for sys.argv[1:]. A command-line
            string, bytes, nonsequence or nonstring element raises TypeError.

    Returns 0 for success/help, 2 for usage, 1 for expected operational failure
    or 130 for interruption. Completed publications and exception notes are
    reported on stderr on failure; they are never rolled back. Unexpected
    programming errors propagate. Help/usage never exit the caller.
    Importing this module performs no parsing, path inspection or CLI execution.
    """
    if argv is not None and (
        isinstance(argv, (str, bytes))
        or not isinstance(argv, Sequence)
        or any(not isinstance(value, str) for value in argv)
    ):
        raise TypeError("argv must be a sequence of strings or None")
    try:
        values = list(sys.argv[1:] if argv is None else argv)
        options = _parser().parse_args(values)
    except _ParserExit as outcome:
        if outcome.message:
            print(outcome.message, file=sys.stderr, end="")
        return outcome.status
    except (MemoryError, KeyboardInterrupt) as error:
        interrupted = isinstance(error, KeyboardInterrupt)
        _diagnostic("Interrupted" if interrupted else "Indexing failed", error, [])
        return 130 if interrupted else 1
    published: list[Path] = []
    try:
        target = Path(options.target)
        stem = (
            Path(options.output)
            if options.output is not None
            else target.parent / target.stem
        )
        sqlite = Path(str(stem) + ".sqlite3")
        raw = Path(str(stem) + ".u64")
        _preflight(target, (sqlite, raw), overwrite=options.overwrite)
        offsets = build_line_index(target)
        write_sqlite_index(offsets, sqlite, overwrite=options.overwrite)
        published.append(sqlite)
        write_raw_index(offsets, raw, overwrite=options.overwrite)
        published.append(raw)
        print(f"Indexed {len(offsets) - 1} lines: {sqlite}; {raw}")
        return 0
    except KeyboardInterrupt as error:
        _diagnostic("Interrupted", error, published)
        return 130
    except (ArchiveLineIndexError, OSError, MemoryError, ValueError) as error:
        _diagnostic("Indexing failed", error, published)
        return 1
