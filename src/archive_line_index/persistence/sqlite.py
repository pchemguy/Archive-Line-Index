"""Dedicated canonical SQLite indexes with transaction and publication ownership."""

from __future__ import annotations

import re
import sqlite3
from array import array
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import NoReturn

from ..errors import InvalidIndexError, PersistenceError
from ..offsets import append_offset, validate_offsets
from ..sources import Source, normalize_source
from .fs import (
    flush_file,
    open_binary_file,
    publish_index_file,
    temporary_sibling,
    validate_destination,
)

_SCHEMA = "CREATE TABLE line_index (offset INTEGER PRIMARY KEY)"


@contextmanager
def _connection(
    database: str, *, readonly: bool = False
) -> Iterator[sqlite3.Connection]:
    connection = (
        sqlite3.connect(database, uri=True) if readonly else sqlite3.connect(database)
    )
    primary: BaseException | None = None
    try:
        yield connection
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            connection.close()
        except BaseException as cleanup:
            if primary is None:
                raise
            primary.add_note(f"SQLite connection cleanup failed: {cleanup!r}")


def _raise_engine_error(error: sqlite3.Error) -> NoReturn:
    code = getattr(error, "sqlite_errorcode", 0) & 0xFF
    kind = (
        InvalidIndexError
        if code in (sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB)
        else PersistenceError
    )
    translated = kind(f"SQLite index operation failed: {error}")
    for note in getattr(error, "__notes__", ()):
        translated.add_note(note)
    raise translated from error


def _check_integrity(connection: sqlite3.Connection) -> None:
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise InvalidIndexError("SQLite integrity check failed")


def _remove_sidecars(temporary: Path, primary: BaseException | None) -> None:
    cleanup_error: BaseException | None = None
    for suffix in ("-journal", "-wal", "-shm"):
        try:
            Path(str(temporary) + suffix).unlink(missing_ok=True)
        except BaseException as error:
            if primary is not None:
                primary.add_note(f"SQLite sidecar cleanup failed: {error!r}")
            elif cleanup_error is None:
                cleanup_error = error
            else:
                cleanup_error.add_note(f"Additional sidecar cleanup failed: {error!r}")
    if cleanup_error is not None:
        raise cleanup_error


def _write_database(temporary: Path, offsets: array[int]) -> None:
    primary: BaseException | None = None
    try:
        with _connection(str(temporary)) as connection:
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN")
            connection.execute(_SCHEMA)
            connection.executemany(
                "INSERT INTO line_index(offset) VALUES (?)",
                ((value,) for value in offsets),
            )
            connection.commit()
            _check_integrity(connection)
            observed = connection.execute(
                "SELECT count(*), min(offset), max(offset) FROM line_index"
            ).fetchone()
            if observed != (len(offsets), offsets[0], offsets[-1]):
                raise InvalidIndexError("SQLite write completeness check failed")
    except BaseException as error:
        primary = error
        raise
    finally:
        _remove_sidecars(temporary, primary)


def write_sqlite_index(
    offsets: array[int], destination: Source, *, overwrite: bool = False
) -> None:
    """Publish a complete dedicated SQLite index from a borrowed canonical array.

    Args:
        offsets: Canonical Q/eight-byte line starts plus EOF, never modified.
        destination: Explicit text filesystem path.
        overwrite: Authorize atomic whole-file replacement, including old tables.

    A transaction commits and integrity/count/bounds checks complete before every
    owned handle is closed. DELETE journaling avoids WAL dependence. Invalid input
    precedes allocation; pre-publication errors preserve an existing destination.
    """
    validate_offsets(offsets)
    path = validate_destination(destination, overwrite=overwrite)
    published = False
    try:
        with temporary_sibling(path) as temporary:
            _write_database(temporary, offsets)
            with open_binary_file(temporary, "rb") as handle:
                flush_file(handle)
            publish_index_file(temporary, path, overwrite=overwrite)
            published = True
    except sqlite3.Error as error:
        _raise_engine_error(error)
    except BaseException as error:
        if published:
            error.add_note(f"Publication already succeeded: {path}")
        raise


def _check_schema(connection: sqlite3.Connection) -> None:
    objects = connection.execute(
        "SELECT type,name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
    ).fetchall()
    if len(objects) != 1 or objects[0][:2] != ("table", "line_index"):
        raise InvalidIndexError("Expected only the dedicated line_index table")
    table = r'(?:line_index|"line_index"|`line_index`|\[line_index\])'
    column = r'(?:offset|"offset"|`offset`|\[offset\])'
    declaration = (
        rf"CREATE\s+TABLE\s+{table}\s*\(\s*{column}\s+INTEGER\s+PRIMARY\s+KEY\s*\)\s*;?"
    )
    if not re.fullmatch(declaration, objects[0][2], flags=re.I):
        raise InvalidIndexError("Noncanonical line_index declaration")
    if connection.execute("PRAGMA table_xinfo(line_index)").fetchall() != [
        (0, "offset", "INTEGER", 0, None, 1, 0)
    ]:
        raise InvalidIndexError("Noncanonical line_index columns or primary key")
    if connection.execute("PRAGMA index_list(line_index)").fetchall():
        raise InvalidIndexError("Unexpected line_index indexes")


def read_sqlite_index(source: Source) -> array[int]:
    """Read a dedicated stable database without mutating it or creating sidecars.

    Returns a new canonical array, including EOF. Schema/content/corruption defects
    raise InvalidIndexError; other engine failures raise PersistenceError with a
    cause. Filesystem acquisition errors retain their ordinary Python types.
    """
    path = normalize_source(source)
    offsets = array("Q")
    if offsets.itemsize != 8:
        raise InvalidIndexError("Native unsigned Q offsets require eight-byte items")
    with open_binary_file(path, "rb"):
        pass
    uri = path.absolute().as_uri() + "?mode=ro&immutable=1"
    try:
        with _connection(uri, readonly=True) as connection:
            _check_integrity(connection)
            _check_schema(connection)
            for (value,) in connection.execute(
                "SELECT offset FROM line_index ORDER BY offset"
            ):
                append_offset(offsets, value)
            validate_offsets(offsets)
        return offsets
    except sqlite3.Error as error:
        # A source removed/denied between the filesystem probe and SQLite opening
        # still has an ordinary filesystem error when the OS can establish it.
        if getattr(error, "sqlite_errorcode", 0) & 0xFF == sqlite3.SQLITE_CANTOPEN:
            with open_binary_file(path, "rb"):
                pass
        _raise_engine_error(error)
