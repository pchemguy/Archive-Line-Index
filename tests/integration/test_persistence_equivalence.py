"""Cross-format persistence equivalence over every supported source family."""

from __future__ import annotations

from array import array
from pathlib import Path
import sqlite3
import struct

import pytest

from archive_line_index import (
    build_line_index,
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)
from archive_line_index.persistence import raw as raw_persistence
from archive_line_index.persistence import sqlite as sqlite_persistence
from tests.helpers.archive_factory import ArchiveMember, write_7z, write_tar, write_zip
from tests.helpers.binary_cases import BINARY_CASES


SOURCE_KINDS = ("plain", "zip", "tar", "7z")


def _write_source(tmp_path: Path, kind: str, name: str, content: bytes) -> Path:
    member = ArchiveMember("nested/data", content)
    if kind == "plain":
        path = tmp_path / f"{name}.data"
        path.write_bytes(content)
        return path
    if kind == "zip":
        return write_zip(tmp_path / f"{name}.zip", [member])
    if kind == "tar":
        return write_tar(tmp_path / f"{name}.tar", [member])
    if kind == "7z":
        return write_7z(tmp_path / f"{name}.7z", [member])
    raise AssertionError(f"unknown source kind: {kind}")


@pytest.mark.parametrize("case", BINARY_CASES, ids=lambda case: case.name)
@pytest.mark.parametrize("source_kind", SOURCE_KINDS)
def test_source_index_round_trips_identically_through_both_formats(
    tmp_path, case, source_kind: str
) -> None:
    source = _write_source(tmp_path, source_kind, case.name, case.content)
    original = build_line_index(
        source,
        skip_utf8_bom=case.skip_bom,
        buffer_size=2,
    )
    sqlite_path = tmp_path / "index.sqlite"
    raw_path = tmp_path / "index.raw"

    write_sqlite_index(original, sqlite_path)
    write_raw_index(original, raw_path)
    from_sqlite = read_sqlite_index(sqlite_path)
    from_raw = read_raw_index(raw_path)

    assert original.typecode == from_sqlite.typecode == from_raw.typecode == "Q"
    assert original.itemsize == from_sqlite.itemsize == from_raw.itemsize == 8
    assert tuple(original) == tuple(from_sqlite) == tuple(from_raw) == case.offsets
    assert len(original) - 1 == len(from_sqlite) - 1 == len(from_raw) - 1
    assert original[-1] == from_sqlite[-1] == from_raw[-1] == len(case.content)

    with sqlite3.connect(sqlite_path) as connection:
        objects = connection.execute(
            "SELECT type, name FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        rows = connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ).fetchall()
    assert objects == [("table", "line_index")]
    assert rows == [(value,) for value in original]
    assert raw_path.read_bytes() == b"".join(
        struct.pack("<Q", value) for value in original
    )


@pytest.mark.parametrize(
    ("writer", "reader", "suffix"),
    [
        (write_sqlite_index, read_sqlite_index, ".sqlite"),
        (write_raw_index, read_raw_index, ".raw"),
    ],
)
def test_repeated_authorized_replacement_is_whole_file(
    tmp_path, writer, reader, suffix: str
) -> None:
    path = tmp_path / f"index{suffix}"

    writer(array("Q", [0, 2]), path)
    writer(array("Q", [3, 8, 13]), path, overwrite=True)
    writer(array("Q", [0]), path, overwrite=True)

    assert list(reader(path)) == [0]
    assert {item.name for item in tmp_path.iterdir()} == {path.name}


@pytest.mark.parametrize(
    ("writer", "module", "suffix"),
    [
        (write_sqlite_index, sqlite_persistence, ".sqlite"),
        (write_raw_index, raw_persistence, ".raw"),
    ],
)
def test_prepublication_failure_preserves_prior_bytes_and_cleans_artifacts(
    tmp_path, monkeypatch, writer, module, suffix: str
) -> None:
    path = tmp_path / f"index{suffix}"
    writer(array("Q", [0, 2]), path)
    before = path.read_bytes()
    failure = OSError("controlled publication failure")

    def fail_publish(*args, **kwargs):
        raise failure

    monkeypatch.setattr(module, "_publish", fail_publish)

    with pytest.raises(OSError) as captured:
        writer(array("Q", [0, 4, 9]), path, overwrite=True)

    assert captured.value is failure
    assert path.read_bytes() == before
    assert {item.name for item in tmp_path.iterdir()} == {path.name}
