"""Tests for validated sequential ZIP member streaming."""

from __future__ import annotations

import io
import zipfile

import pytest

from archive_line_index.backends.zip import open_zip_backend
from archive_line_index.errors import (
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
)
from archive_line_index.sources import open_source
from archive_line_index.stream import ContentStream
from tests.helpers.archive_factory import ArchiveMember, write_zip


def _read_backend(path_or_stream, size: int = 3) -> bytes:
    backend = open_zip_backend(open_source(path_or_stream))
    chunks = []
    try:
        while chunk := backend.read(size):
            chunks.append(chunk)
        assert backend.completed
        return b"".join(chunks)
    finally:
        backend.close()


def test_path_streams_nested_member_with_directories(tmp_path) -> None:
    path = write_zip(
        tmp_path / "data.zip",
        [
            ArchiveMember("nested", kind="directory"),
            ArchiveMember("nested/data.jsonl", b"a\nb"),
        ],
    )
    assert _read_backend(path, 1) == b"a\nb"


def test_seekable_caller_stream_remains_open() -> None:
    encoded = io.BytesIO()
    with zipfile.ZipFile(encoded, "w") as archive:
        archive.writestr("data", b"payload")
    source = io.BytesIO(encoded.getvalue())

    assert _read_backend(source) == b"payload"
    assert not source.closed


def test_empty_member_is_valid(tmp_path) -> None:
    path = write_zip(tmp_path / "empty.zip", [ArchiveMember("empty", b"")])
    backend = open_zip_backend(open_source(path))
    assert backend.declared_size == 0
    assert backend.read(1) == b""
    assert backend.completed
    backend.close()


@pytest.mark.parametrize(
    "members",
    [
        [ArchiveMember("directory", kind="directory")],
        [ArchiveMember("a", b"a"), ArchiveMember("b", b"b")],
        [ArchiveMember("data", b"x"), ArchiveMember("__MACOSX/meta", b"m")],
    ],
)
def test_zero_multiple_and_metadata_files_are_rejected(tmp_path, members) -> None:
    path = write_zip(tmp_path / "structure.zip", members)
    with pytest.raises(ArchiveStructureError, match="exactly one"):
        open_zip_backend(open_source(path))


def test_symlink_entry_is_rejected_even_with_one_file(tmp_path) -> None:
    path = write_zip(
        tmp_path / "special.zip",
        [
            ArchiveMember("data", b"payload"),
            ArchiveMember("link", kind="symlink", target="data"),
        ],
    )
    with pytest.raises(ArchiveStructureError, match="unsupported"):
        open_zip_backend(open_source(path))


def test_invalid_and_truncated_archives_are_open_failures(tmp_path) -> None:
    invalid = tmp_path / "invalid.zip"
    invalid.write_bytes(b"PK\x03\x04not-a-zip")
    with pytest.raises(InvalidArchiveError) as captured:
        open_zip_backend(open_source(invalid))
    assert isinstance(captured.value.__cause__, zipfile.BadZipFile)

    valid = write_zip(tmp_path / "valid.zip", [ArchiveMember("data", b"payload")])
    truncated = tmp_path / "truncated.zip"
    truncated.write_bytes(valid.read_bytes()[:-12])
    with pytest.raises(InvalidArchiveError):
        open_zip_backend(open_source(truncated))


def test_crc_failure_is_translated_during_read(tmp_path) -> None:
    path = tmp_path / "crc.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("data", b"payload")
    content = bytearray(path.read_bytes())
    local = content.index(b"PK\x03\x04")
    name_length = int.from_bytes(content[local + 26 : local + 28], "little")
    extra_length = int.from_bytes(content[local + 28 : local + 30], "little")
    data_start = local + 30 + name_length + extra_length
    content[data_start] ^= 0xFF
    path.write_bytes(content)

    backend = open_zip_backend(open_source(path))
    with pytest.raises(ExtractionError) as captured:
        backend.read(100)
    assert isinstance(captured.value.__cause__, zipfile.BadZipFile)


def test_declared_size_limit_rejects_and_preserves_caller(tmp_path) -> None:
    path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", b"payload")])
    source = io.BytesIO(path.read_bytes())
    backend = open_zip_backend(open_source(source))
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)
    assert not source.closed


def test_early_close_is_idempotent_and_preserves_caller(tmp_path) -> None:
    path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", b"payload")])
    source = io.BytesIO(path.read_bytes())
    backend = open_zip_backend(open_source(source))
    assert backend.read(1) == b"p"
    backend.close()
    backend.close()
    assert not source.closed
    with pytest.raises(ValueError):
        backend.read(1)


def test_nonseekable_zip_is_rejected_without_closing_caller(tmp_path) -> None:
    path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", b"payload")])

    class NonSeekable(io.BytesIO):
        def seekable(self) -> bool:
            return False

    source = NonSeekable(path.read_bytes())
    with pytest.raises(InvalidArchiveError, match="seekable"):
        open_zip_backend(open_source(source))
    assert not source.closed
