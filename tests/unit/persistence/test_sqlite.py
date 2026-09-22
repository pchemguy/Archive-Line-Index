"""Tests for the dedicated SQLite line-index persistence format."""

from __future__ import annotations

from array import array
import sqlite3

import pytest

from archive_line_index.errors import InvalidIndexError, PersistenceError
from archive_line_index.offsets import MAX_OFFSET
from archive_line_index.persistence import sqlite as sqlite_persistence


def _offsets(*values: int) -> array:
    return array("Q", values)


@pytest.mark.parametrize(
    "values",
    [[0], [3], [0, 2, 5, 9], list(range(0, 20_000, 2))],
)
def test_write_creates_exact_schema_and_rows(tmp_path, values: list[int]) -> None:
    destination = tmp_path / "index.sqlite"

    sqlite_persistence.write_sqlite_index(_offsets(*values), destination)

    with sqlite3.connect(destination) as connection:
        objects = connection.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        columns = connection.execute("PRAGMA table_info(line_index)").fetchall()
        rows = connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ).fetchall()
    assert objects == [
        (
            "table",
            "line_index",
            "CREATE TABLE line_index (\n    offset INTEGER PRIMARY KEY\n)",
        )
    ]
    assert columns == [(0, "offset", "INTEGER", 0, None, 1)]
    assert rows == [(value,) for value in values]


def test_existing_destination_is_protected_without_temporary_file(tmp_path) -> None:
    destination = tmp_path / "index.sqlite"
    destination.write_bytes(b"original")

    with pytest.raises(FileExistsError):
        sqlite_persistence.write_sqlite_index(_offsets(0), destination)

    assert destination.read_bytes() == b"original"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


def test_overwrite_replaces_entire_existing_file(tmp_path) -> None:
    destination = tmp_path / "index.sqlite"
    destination.write_bytes(b"original")

    sqlite_persistence.write_sqlite_index(
        _offsets(0, 4, 8), destination, overwrite=True
    )

    with sqlite3.connect(destination) as connection:
        assert connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ).fetchall() == [(0,), (4,), (8,)]


@pytest.mark.parametrize(
    "offsets",
    [array("Q"), _offsets(1), _offsets(0, 0), _offsets(0, MAX_OFFSET + 1)],
)
def test_invalid_offsets_fail_before_temporary_creation(
    tmp_path, monkeypatch, offsets: array
) -> None:
    def unexpected_temp(*args, **kwargs):
        raise AssertionError("temporary file created before validation")

    monkeypatch.setattr(sqlite_persistence.tempfile, "mkstemp", unexpected_temp)

    with pytest.raises(InvalidIndexError):
        sqlite_persistence.write_sqlite_index(offsets, tmp_path / "index.sqlite")


@pytest.mark.parametrize("overwrite", [None, 0, 1, "yes"])
def test_overwrite_must_be_bool(tmp_path, overwrite) -> None:
    with pytest.raises(TypeError, match="overwrite"):
        sqlite_persistence.write_sqlite_index(
            _offsets(0), tmp_path / "index.sqlite", overwrite=overwrite
        )


def test_missing_destination_directory_raises_ordinary_os_error(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        sqlite_persistence.write_sqlite_index(
            _offsets(0), tmp_path / "missing" / "index.sqlite"
        )


@pytest.mark.parametrize("stage", ["insert", "validate", "publish"])
def test_prepublication_failure_preserves_destination_and_cleans_temp(
    tmp_path, monkeypatch, stage: str
) -> None:
    destination = tmp_path / "index.sqlite"
    destination.write_bytes(b"original")
    failure = RuntimeError(f"controlled {stage} failure")

    if stage == "insert":
        monkeypatch.setattr(
            sqlite_persistence,
            "_insert_offsets",
            lambda *args, **kwargs: (_ for _ in ()).throw(failure),
        )
    elif stage == "validate":
        monkeypatch.setattr(
            sqlite_persistence,
            "_validate_written_database",
            lambda *args, **kwargs: (_ for _ in ()).throw(failure),
        )
    else:
        monkeypatch.setattr(
            sqlite_persistence,
            "_publish",
            lambda *args, **kwargs: (_ for _ in ()).throw(failure),
        )

    with pytest.raises(RuntimeError) as captured:
        sqlite_persistence.write_sqlite_index(
            _offsets(0, 4), destination, overwrite=True
        )

    assert captured.value is failure
    assert destination.read_bytes() == b"original"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


def test_sqlite_engine_failure_is_translated_with_cause(tmp_path, monkeypatch) -> None:
    failure = sqlite3.OperationalError("controlled connect failure")

    def fail_connect(*args, **kwargs):
        raise failure

    monkeypatch.setattr(sqlite_persistence.sqlite3, "connect", fail_connect)

    with pytest.raises(PersistenceError) as captured:
        sqlite_persistence.write_sqlite_index(
            _offsets(0), tmp_path / "index.sqlite"
        )

    assert captured.value.__cause__ is failure
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("values", [[0], [3], [0, 4, 9]])
def test_read_round_trips_written_database(tmp_path, values: list[int]) -> None:
    path = tmp_path / "index.sqlite"
    sqlite_persistence.write_sqlite_index(_offsets(*values), path)

    loaded = sqlite_persistence.read_sqlite_index(path)

    assert loaded.typecode == "Q"
    assert loaded.itemsize == 8
    assert list(loaded) == values


def test_read_missing_file_raises_file_not_found(tmp_path) -> None:
    path = tmp_path / "missing.sqlite"

    with pytest.raises(FileNotFoundError):
        sqlite_persistence.read_sqlite_index(path)

    assert not path.exists()


@pytest.mark.parametrize(
    "schema",
    [
        "CREATE TABLE line_index(value INTEGER PRIMARY KEY)",
        "CREATE TABLE line_index(offset TEXT PRIMARY KEY)",
        "CREATE TABLE line_index(offset INTEGER)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY, extra INTEGER)",
        "CREATE TABLE other(offset INTEGER PRIMARY KEY)",
    ],
)
def test_read_rejects_noncanonical_schema(tmp_path, schema: str) -> None:
    path = tmp_path / "index.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute(schema)

    with pytest.raises(InvalidIndexError, match="schema"):
        sqlite_persistence.read_sqlite_index(path)


@pytest.mark.parametrize(
    "extra_sql",
    [
        "CREATE TABLE extra(value INTEGER)",
        "CREATE INDEX extra_index ON line_index(offset)",
        "CREATE VIEW extra_view AS SELECT offset FROM line_index",
        "CREATE TRIGGER extra_trigger AFTER INSERT ON line_index BEGIN SELECT 1; END",
    ],
)
def test_read_rejects_extra_user_schema_objects(tmp_path, extra_sql: str) -> None:
    path = tmp_path / "index.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE line_index(offset INTEGER PRIMARY KEY)")
        connection.execute("INSERT INTO line_index VALUES (0)")
        connection.execute(extra_sql)

    with pytest.raises(InvalidIndexError, match="schema"):
        sqlite_persistence.read_sqlite_index(path)


def test_read_rejects_empty_table(tmp_path) -> None:
    path = tmp_path / "index.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE line_index(offset INTEGER PRIMARY KEY)")

    with pytest.raises(InvalidIndexError, match="EOF sentinel"):
        sqlite_persistence.read_sqlite_index(path)


@pytest.mark.parametrize("values", [[1], [0, -1]])
def test_read_rejects_invalid_offset_content(tmp_path, values: list[int]) -> None:
    path = tmp_path / "index.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE line_index(offset INTEGER PRIMARY KEY)")
        connection.executemany(
            "INSERT INTO line_index VALUES (?)", ((value,) for value in values)
        )

    with pytest.raises(InvalidIndexError):
        sqlite_persistence.read_sqlite_index(path)


def test_read_corrupt_database_is_persistence_error_with_cause(tmp_path) -> None:
    path = tmp_path / "index.sqlite"
    path.write_bytes(b"not a SQLite database")

    with pytest.raises(PersistenceError) as captured:
        sqlite_persistence.read_sqlite_index(path)

    assert isinstance(captured.value.__cause__, sqlite3.Error)
