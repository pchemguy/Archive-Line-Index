"""Integration coverage for the public persistence surface."""

from __future__ import annotations

from array import array
import sqlite3

import pytest

import archive_line_index
from archive_line_index import InvalidIndexError, PersistenceError
from archive_line_index.persistence import raw as raw_persistence
from archive_line_index.persistence import sqlite as sqlite_persistence


PUBLIC_NAMES = {
    "ArchiveLineIndexError",
    "ArchiveStructureError",
    "ContentStream",
    "DEFAULT_BUFFER_SIZE",
    "ExtractionError",
    "InvalidArchiveError",
    "InvalidIndexError",
    "PersistenceError",
    "SizeLimitExceededError",
    "Source",
    "UnsupportedFormatError",
    "build_line_index",
    "open_content_stream",
    "read_raw_index",
    "read_sqlite_index",
    "scan_line_offsets",
    "write_raw_index",
    "write_sqlite_index",
}


def test_package_exports_exact_documented_public_surface() -> None:
    assert set(archive_line_index.__all__) == PUBLIC_NAMES
    assert all(hasattr(archive_line_index, name) for name in PUBLIC_NAMES)


@pytest.mark.parametrize("kind", ["sqlite", "raw"])
def test_public_persistence_round_trip(tmp_path, kind: str) -> None:
    offsets = array("Q", [0, 4, 9])
    path = tmp_path / f"index.{kind}"
    writer = getattr(archive_line_index, f"write_{kind}_index")
    reader = getattr(archive_line_index, f"read_{kind}_index")

    writer(offsets, path)

    loaded = reader(path)
    assert loaded.typecode == "Q"
    assert loaded.itemsize == 8
    assert loaded == offsets


@pytest.mark.parametrize("name", ["write_sqlite_index", "write_raw_index"])
def test_public_writers_require_explicit_destination(name: str) -> None:
    with pytest.raises(TypeError, match="destination"):
        getattr(archive_line_index, name)(array("Q", [0]))


@pytest.mark.parametrize(
    ("writer_name", "module"),
    [
        ("write_sqlite_index", sqlite_persistence),
        ("write_raw_index", raw_persistence),
    ],
)
def test_public_validation_precedes_temporary_creation(
    tmp_path, monkeypatch, writer_name: str, module
) -> None:
    def unexpected_temp(*args, **kwargs):
        raise AssertionError("temporary file created before validation")

    monkeypatch.setattr(module.tempfile, "mkstemp", unexpected_temp)

    with pytest.raises(InvalidIndexError):
        getattr(archive_line_index, writer_name)(
            array("Q"), tmp_path / "index"
        )


@pytest.mark.parametrize("name", ["read_sqlite_index", "read_raw_index"])
def test_public_readers_preserve_file_not_found(tmp_path, name: str) -> None:
    with pytest.raises(FileNotFoundError):
        getattr(archive_line_index, name)(tmp_path / "missing")


def test_public_sqlite_translation_retains_engine_cause(tmp_path) -> None:
    path = tmp_path / "corrupt.sqlite"
    path.write_bytes(b"not a sqlite database")

    with pytest.raises(PersistenceError) as captured:
        archive_line_index.read_sqlite_index(path)

    assert isinstance(captured.value.__cause__, sqlite3.DatabaseError)
