"""Failure-safe SQLite persistence for canonical line offsets."""

from __future__ import annotations

from array import array
import os
from os import PathLike
from pathlib import Path
import sqlite3
import tempfile

from ..errors import InvalidIndexError, PersistenceError
from ..offsets import make_offset_array, validate_offset_array


_SCHEMA = """CREATE TABLE line_index (
    offset INTEGER PRIMARY KEY
)"""


def write_sqlite_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Write a complete canonical offset sequence to a dedicated database."""

    validated = validate_offset_array(offsets)
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a bool")
    path = _normalize_path(destination, "destination")
    if not overwrite and path.exists():
        raise FileExistsError(path)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        _write_database(temporary, validated)
        _validate_written_database(temporary, validated)
        _flush_file(temporary)
        _publish(temporary, path, overwrite=overwrite)
    except BaseException as primary:
        try:
            temporary.unlink(missing_ok=True)
        except OSError as cleanup_error:
            primary.add_note(f"temporary cleanup failed: {cleanup_error}")
        raise


def read_sqlite_index(source: str | PathLike[str]) -> array:
    """Load and strictly validate a dedicated SQLite offset database."""

    path = _normalize_path(source, "source")
    if not path.exists():
        raise FileNotFoundError(path)

    connection: sqlite3.Connection | None = None
    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        _validate_read_schema(connection)
        values = []
        for (value,) in connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidIndexError("SQLite offsets must be integers")
            values.append(value)
        return make_offset_array(values)
    except InvalidIndexError:
        raise
    except sqlite3.Error as exc:
        raise PersistenceError("failed to read SQLite index") from exc
    finally:
        if connection is not None:
            connection.close()


def _write_database(path: Path, offsets: array) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(path)
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(_SCHEMA)
        _insert_offsets(connection, offsets)
        connection.commit()
    except sqlite3.Error as exc:
        if connection is not None:
            try:
                connection.rollback()
            except sqlite3.Error:
                pass
        raise PersistenceError("failed to write SQLite index") from exc
    finally:
        if connection is not None:
            connection.close()


def _insert_offsets(connection: sqlite3.Connection, offsets: array) -> None:
    connection.executemany(
        "INSERT INTO line_index(offset) VALUES (?)",
        ((value,) for value in offsets),
    )


def _validate_written_database(path: Path, offsets: array) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(path)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity != ("ok",):
            raise PersistenceError("SQLite integrity validation failed")
        count, minimum, maximum = connection.execute(
            "SELECT count(*), min(offset), max(offset) FROM line_index"
        ).fetchone()
        if (count, minimum, maximum) != (
            len(offsets),
            offsets[0],
            offsets[-1],
        ):
            raise PersistenceError("SQLite boundary validation failed")
    except sqlite3.Error as exc:
        raise PersistenceError("failed to validate SQLite index") from exc
    finally:
        if connection is not None:
            connection.close()


def _validate_read_schema(connection: sqlite3.Connection) -> None:
    objects = connection.execute(
        "SELECT type, name FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()
    if objects != [("table", "line_index")]:
        raise InvalidIndexError("SQLite index has a noncanonical schema")

    columns = connection.execute("PRAGMA table_info(line_index)").fetchall()
    if columns != [(0, "offset", "INTEGER", 0, None, 1)]:
        raise InvalidIndexError("SQLite index has a noncanonical schema")

    table_rows = connection.execute("PRAGMA table_list").fetchall()
    line_index_rows = [row for row in table_rows if row[1] == "line_index"]
    if len(line_index_rows) != 1:
        raise InvalidIndexError("SQLite index has a noncanonical schema")
    table = line_index_rows[0]
    if table[2:] != ("table", 1, 0, 0):
        raise InvalidIndexError("SQLite index has a noncanonical schema")


def _flush_file(path: Path) -> None:
    with path.open("rb") as stream:
        os.fsync(stream.fileno())


def _publish(temporary: Path, destination: Path, *, overwrite: bool) -> None:
    if overwrite:
        os.replace(temporary, destination)
        return
    if destination.exists():
        raise FileExistsError(destination)
    os.link(temporary, destination)
    temporary.unlink()


def _normalize_path(value: str | PathLike[str], name: str) -> Path:
    if not isinstance(value, (str, os.PathLike)):
        raise TypeError(f"{name} must be a filesystem path")
    path = os.fspath(value)
    if not isinstance(path, str):
        raise TypeError(f"{name} paths must resolve to str, not bytes")
    return Path(path)
