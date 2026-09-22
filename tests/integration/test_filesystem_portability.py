"""Portable filesystem, publication, and owned-handle integration checks."""

from __future__ import annotations

from array import array
import builtins
import io
import os
from pathlib import Path
import zipfile

import pytest

from archive_line_index import (
    ExtractionError,
    InvalidArchiveError,
    open_content_stream,
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)
from archive_line_index.persistence import raw as raw_persistence
from archive_line_index.persistence import sqlite as sqlite_persistence


WRITERS = (
    (raw_persistence, write_raw_index, ".raw"),
    (sqlite_persistence, write_sqlite_index, ".sqlite"),
)


class StringPath:
    """Minimal path-like value that resolves to a Unicode string path."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def __fspath__(self) -> str:
        return str(self.path)


@pytest.mark.parametrize(
    ("writer", "reader", "suffix"),
    [
        (write_raw_index, read_raw_index, ".raw"),
        (write_sqlite_index, read_sqlite_index, ".sqlite"),
    ],
)
def test_unicode_path_like_values_round_trip(
    tmp_path, writer, reader, suffix: str
) -> None:
    directory = tmp_path / "данные 日本語"
    directory.mkdir()
    source = directory / "строки.txt"
    source.write_bytes(b"alpha\nbeta")
    with open_content_stream(StringPath(source)) as stream:
        assert stream.read() == b"alpha\nbeta"

    destination = directory / f"индекс{suffix}"
    offsets = array("Q", [0, 6, 10])
    writer(offsets, StringPath(destination))

    assert reader(StringPath(destination)) == offsets


@pytest.mark.parametrize(("module", "writer", "suffix"), WRITERS)
def test_temporary_file_is_a_hidden_destination_sibling(
    tmp_path, monkeypatch, module, writer, suffix: str
) -> None:
    destination = tmp_path / f"index{suffix}"
    observed = {}
    real_mkstemp = module.tempfile.mkstemp

    def tracking_mkstemp(*args, **kwargs):
        observed.update(kwargs)
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr(module.tempfile, "mkstemp", tracking_mkstemp)

    writer(array("Q", [0, 4]), destination)

    assert Path(observed["dir"]) == destination.parent
    assert observed["prefix"] == f".{destination.name}."
    assert observed["suffix"] == ".tmp"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


@pytest.mark.parametrize(("module", "writer", "suffix"), WRITERS)
def test_permission_denied_during_replacement_preserves_destination_and_cleans_temp(
    tmp_path, monkeypatch, module, writer, suffix: str
) -> None:
    destination = tmp_path / f"index{suffix}"
    destination.write_bytes(b"original")
    failure = PermissionError("controlled replacement denial")

    def deny_replace(*args, **kwargs):
        raise failure

    monkeypatch.setattr(module.os, "replace", deny_replace)

    with pytest.raises(PermissionError) as captured:
        writer(array("Q", [0, 4]), destination, overwrite=True)

    assert captured.value is failure
    assert destination.read_bytes() == b"original"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


@pytest.mark.parametrize(("module", "writer", "suffix"), WRITERS)
def test_permission_denied_during_no_overwrite_publish_cleans_temp(
    tmp_path, monkeypatch, module, writer, suffix: str
) -> None:
    destination = tmp_path / f"index{suffix}"
    failure = PermissionError("controlled hard-link denial")

    def deny_link(*args, **kwargs):
        raise failure

    monkeypatch.setattr(module.os, "link", deny_link)

    with pytest.raises(PermissionError) as captured:
        writer(array("Q", [0, 4]), destination)

    assert captured.value is failure
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(("module", "writer", "suffix"), WRITERS)
def test_replacing_an_open_destination_follows_host_semantics(
    tmp_path, module, writer, suffix: str
) -> None:
    destination = tmp_path / f"index{suffix}"
    destination.write_bytes(b"original")

    with destination.open("rb") as original:
        if os.name == "nt":
            with pytest.raises(OSError):
                writer(array("Q", [0, 4]), destination, overwrite=True)
            assert destination.read_bytes() == b"original"
        else:
            writer(array("Q", [0, 4]), destination, overwrite=True)
            assert original.read() == b"original"

    assert not any(
        path.name.startswith(f".{destination.name}.")
        for path in tmp_path.iterdir()
    )


def test_sqlite_success_leaves_no_journal_or_wal_sidecars(tmp_path) -> None:
    destination = tmp_path / "index.sqlite"
    write_sqlite_index(array("Q", [0, 4, 9]), destination)
    write_sqlite_index(array("Q", [0, 5]), destination, overwrite=True)

    assert read_sqlite_index(destination) == array("Q", [0, 5])
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


@pytest.mark.parametrize(
    "content",
    [b"PK\x03\x04broken", b"\x1f\x8bbroken", b"7z\xbc\xaf\x27\x1cbroken"],
)
def test_archive_open_failure_closes_owned_path_handles(
    tmp_path, monkeypatch, content: bytes
) -> None:
    path = tmp_path / "invalid"
    path.write_bytes(content)
    opened = []
    real_builtin_open = builtins.open
    real_io_open = io.open

    def record_target_handle(file, mode, result):
        if os.fspath(file) == os.fspath(path) and mode == "rb":
            opened.append(result)
        return result

    def tracking_builtin_open(file, mode="r", *args, **kwargs):
        return record_target_handle(
            file,
            mode,
            real_builtin_open(file, mode, *args, **kwargs),
        )

    def tracking_io_open(file, mode="r", *args, **kwargs):
        return record_target_handle(
            file,
            mode,
            real_io_open(file, mode, *args, **kwargs),
        )

    monkeypatch.setattr(builtins, "open", tracking_builtin_open)
    monkeypatch.setattr(io, "open", tracking_io_open)

    with pytest.raises(InvalidArchiveError):
        open_content_stream(path)

    assert opened
    assert all(stream.closed for stream in opened)
    moved = path.with_name("moved")
    path.replace(moved)
    moved.unlink()


def test_zip_processing_failure_closes_backend_handles_before_caller_cleanup(
    tmp_path,
) -> None:
    path = tmp_path / "crc.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("data", b"payload")
    content = bytearray(path.read_bytes())
    local = content.index(b"PK\x03\x04")
    name_length = int.from_bytes(content[local + 26 : local + 28], "little")
    extra_length = int.from_bytes(content[local + 28 : local + 30], "little")
    content[local + 30 + name_length + extra_length] ^= 0xFF
    path.write_bytes(content)

    stream = open_content_stream(path)
    backend = stream._backend
    archive = backend._archive
    member = backend._member

    assert archive is not None
    assert member is not None
    with pytest.raises(ExtractionError):
        stream.read()

    assert stream.closed
    assert member.closed
    assert archive.fp is None
    moved = path.with_name("moved.zip")
    path.replace(moved)
    moved.unlink()


def test_source_permission_error_is_preserved(tmp_path, monkeypatch) -> None:
    path = tmp_path / "denied.txt"
    path.write_bytes(b"payload")
    failure = PermissionError("controlled source denial")
    real_open = builtins.open

    def deny_target(file, mode="r", *args, **kwargs):
        if os.fspath(file) == os.fspath(path) and mode == "rb":
            raise failure
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", deny_target)

    with pytest.raises(PermissionError) as captured:
        open_content_stream(path)

    assert captured.value is failure
