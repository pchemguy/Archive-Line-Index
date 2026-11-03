"""Canonical SQLite storage, transaction completeness and read-only validation."""

from __future__ import annotations

import sqlite3
from array import array
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.errors import InvalidIndexError, PersistenceError
from archive_line_index.persistence.sqlite import write_sqlite_index


@pytest.mark.parametrize(
    "values", [[0], [3], [0, 3], [3, 7, 9], [0, (1 << 63) - 1], list(range(10000))]
)
def test_writer_schema_values_integrity_and_no_sidecars(
    tmp_path: Path, values: list[int]
) -> None:
    path = tmp_path / "index.sqlite3"
    offsets = array("Q", values)
    write_sqlite_index(offsets, path)
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT type,name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
        ).fetchall() == [("table", "line_index")]
        assert connection.execute("PRAGMA table_info(line_index)").fetchall() == [
            (0, "offset", "INTEGER", 0, None, 1)
        ]
        assert connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ).fetchall() == [(v,) for v in values]
        assert connection.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert connection.execute("PRAGMA journal_mode").fetchone() == ("delete",)
    finally:
        connection.close()
    assert offsets.tolist() == values and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    "offsets,overwrite,exc",
    [
        (array("Q"), False, InvalidIndexError),
        (array("I", [0]), False, TypeError),
        (array("Q", [0]), 1, TypeError),
    ],
)
def test_writer_invalid_inputs_do_not_allocate(
    tmp_path: Path, offsets: object, overwrite: object, exc: type[Exception]
) -> None:
    with (
        patch(
            "archive_line_index.persistence.sqlite.temporary_sibling",
            side_effect=AssertionError("allocated"),
        ),
        pytest.raises(exc),
    ):
        write_sqlite_index(offsets, tmp_path / "p", overwrite=overwrite)  # type: ignore[arg-type]


def test_writer_protection_and_full_replacement(tmp_path: Path) -> None:
    path = tmp_path / "index"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE unrelated (value TEXT)")
    connection.close()
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        write_sqlite_index(array("Q", [0]), path)
    assert path.read_bytes() == before
    write_sqlite_index(array("Q", [3]), path, overwrite=True)
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
        ).fetchall() == [("line_index",)]
        assert connection.execute("SELECT offset FROM line_index").fetchall() == [(3,)]
    finally:
        connection.close()


def test_engine_failure_keeps_previous_file_and_cause(tmp_path: Path) -> None:
    path = tmp_path / "index"
    path.write_bytes(b"previous")
    error = sqlite3.OperationalError("engine fault")
    with (
        patch(
            "archive_line_index.persistence.sqlite.sqlite3.connect", side_effect=error
        ),
        pytest.raises(PersistenceError) as caught,
    ):
        write_sqlite_index(array("Q", [0]), path, overwrite=True)
    assert caught.value.__cause__ is error
    assert path.read_bytes() == b"previous" and list(tmp_path.iterdir()) == [path]


def test_failure_after_transaction_commit_does_not_publish(tmp_path: Path) -> None:
    path = tmp_path / "index"
    path.write_bytes(b"previous")
    with (
        patch(
            "archive_line_index.persistence.sqlite._check_integrity",
            side_effect=InvalidIndexError("integrity fault"),
        ),
        pytest.raises(InvalidIndexError),
    ):
        write_sqlite_index(array("Q", [0, 8]), path, overwrite=True)
    assert path.read_bytes() == b"previous" and list(tmp_path.iterdir()) == [path]


def test_sqlite_cleanup_failure_after_publication_is_explicit(tmp_path: Path) -> None:
    path = tmp_path / "index"
    real_unlink = Path.unlink

    def fail_temporary(p: Path, missing_ok: bool = False) -> None:
        if p.suffix == ".tmp":
            raise PermissionError("temp cleanup")
        real_unlink(p, missing_ok=missing_ok)

    with (
        patch.object(Path, "unlink", fail_temporary),
        pytest.raises(PermissionError) as caught,
    ):
        write_sqlite_index(array("Q", [0, 8]), path)
    assert any("Publication already succeeded" in n for n in caught.value.__notes__)
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ).fetchall() == [(0,), (8,)]
    finally:
        connection.close()
    for p in tmp_path.glob(".*.tmp"):
        p.unlink()


@pytest.mark.parametrize("values", [[0], [3], [0, 4, 7], [3, 8], list(range(10000))])
def test_reader_roundtrip_is_read_only(tmp_path: Path, values: list[int]) -> None:
    from archive_line_index.persistence.sqlite import read_sqlite_index

    path = tmp_path / "name with # space.sqlite3"
    original = array("Q", values)
    write_sqlite_index(original, path)
    before = path.read_bytes()
    restored = read_sqlite_index(path)
    assert restored == original and restored is not original
    assert path.read_bytes() == before and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    "schema",
    [
        "CREATE TABLE other(offset INTEGER PRIMARY KEY)",
        "CREATE TABLE line_index(offset INT PRIMARY KEY)",
        "CREATE TABLE line_index(offset INTEGER)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY, extra TEXT)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY) WITHOUT ROWID",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY DESC)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY CHECK(offset>=0))",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY); CREATE TABLE extra(x)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY); CREATE INDEX extra ON line_index(offset)",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY); CREATE VIEW extra AS SELECT offset FROM line_index",
        "CREATE TABLE line_index(offset INTEGER PRIMARY KEY); CREATE TRIGGER extra AFTER INSERT ON line_index BEGIN SELECT 1; END",
    ],
)
def test_reader_rejects_changed_schema_without_modification(
    tmp_path: Path, schema: str
) -> None:
    from archive_line_index.persistence.sqlite import read_sqlite_index

    path = tmp_path / "bad"
    connection = sqlite3.connect(path)
    connection.executescript(schema)
    connection.close()
    before = path.read_bytes()
    with pytest.raises(InvalidIndexError):
        read_sqlite_index(path)
    assert path.read_bytes() == before and list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("values", [[], [1], [-1, 0], [3, 7, 9]])
def test_reader_validates_ordered_model(tmp_path: Path, values: list[int]) -> None:
    from archive_line_index.persistence.sqlite import read_sqlite_index

    path = tmp_path / "p"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE line_index(offset INTEGER PRIMARY KEY)")
    connection.executemany(
        "INSERT INTO line_index VALUES (?)", [(v,) for v in reversed(values)]
    )
    connection.commit()
    connection.close()
    if values == [3, 7, 9]:
        assert read_sqlite_index(path).tolist() == values
    else:
        with pytest.raises(InvalidIndexError):
            read_sqlite_index(path)


def test_reader_corruption_missing_and_engine_failure_categories(
    tmp_path: Path,
) -> None:
    from archive_line_index.persistence.sqlite import read_sqlite_index

    path = tmp_path / "p"
    with pytest.raises(FileNotFoundError):
        read_sqlite_index(path)
    path.write_bytes(b"not a database")
    with pytest.raises(InvalidIndexError) as caught:
        read_sqlite_index(path)
    assert isinstance(caught.value.__cause__, sqlite3.Error)
    error = sqlite3.OperationalError("engine unavailable")
    with (
        patch(
            "archive_line_index.persistence.sqlite.sqlite3.connect", side_effect=error
        ),
        pytest.raises(PersistenceError) as caught,
    ):
        read_sqlite_index(path)
    assert caught.value.__cause__ is error


def test_user_object_resembling_internal_prefix_is_not_hidden(tmp_path: Path) -> None:
    from archive_line_index.persistence.sqlite import read_sqlite_index

    path = tmp_path / "p"
    write_sqlite_index(array("Q", [0, 9]), path)
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE sqliteXextra(value TEXT)")
    connection.close()
    with pytest.raises(InvalidIndexError):
        read_sqlite_index(path)


def test_transaction_failure_keeps_primary_when_connection_cleanup_fails(
    tmp_path: Path,
) -> None:
    real_connect = sqlite3.connect

    class FaultyConnection(sqlite3.Connection):
        def executemany(self, sql: str, parameters: object) -> sqlite3.Cursor:
            raise sqlite3.OperationalError("insert primary")

        def close(self) -> None:
            super().close()
            raise sqlite3.OperationalError("close cleanup")

    def connect(database: str) -> sqlite3.Connection:
        return real_connect(database, factory=FaultyConnection)

    destination = tmp_path / "p"
    destination.write_bytes(b"previous")
    with (
        patch("archive_line_index.persistence.sqlite.sqlite3.connect", connect),
        pytest.raises(PersistenceError) as caught,
    ):
        write_sqlite_index(array("Q", [0, 8]), destination, overwrite=True)
    assert "insert primary" in str(caught.value.__cause__)
    assert any("close cleanup" in n for n in caught.value.__notes__)
    assert destination.read_bytes() == b"previous" and list(tmp_path.iterdir()) == [
        destination
    ]


def test_sidecar_cleanup_is_owned_and_preserves_primary(tmp_path: Path) -> None:
    destination = tmp_path / "p"
    unrelated = tmp_path / "p-wal"
    unrelated.write_bytes(b"unrelated")
    primary = sqlite3.OperationalError("build primary")
    real_unlink = Path.unlink

    def fail_sidecar(path: Path, missing_ok: bool = False) -> None:
        if str(path).endswith(".tmp-journal"):
            raise PermissionError("sidecar cleanup")
        real_unlink(path, missing_ok=missing_ok)

    with (
        patch(
            "archive_line_index.persistence.sqlite._check_integrity",
            side_effect=primary,
        ),
        patch.object(Path, "unlink", fail_sidecar),
        pytest.raises(PersistenceError) as caught,
    ):
        write_sqlite_index(array("Q", [0]), destination)
    assert caught.value.__cause__ is primary
    assert any("sidecar cleanup" in n for n in caught.value.__notes__)
    assert unrelated.read_bytes() == b"unrelated" and not destination.exists()
    assert list(tmp_path.iterdir()) == [unrelated]
