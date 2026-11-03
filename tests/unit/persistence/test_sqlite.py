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
