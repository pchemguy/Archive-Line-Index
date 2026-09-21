"""Tests for validated sequential ZIP member streaming."""

from __future__ import annotations

import zipfile

import pytest

from archive_line_index.backends.zip import open_zip_backend
from archive_line_index.errors import (
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
)
from archive_line_index.stream import ContentStream
from tests.helpers.archive_factory import ArchiveMember, write_zip


def _read_backend(path, size: int = 3) -> bytes:
    backend = open_zip_backend(str(path))
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


def test_empty_member_is_valid(tmp_path) -> None:
    path = write_zip(tmp_path / "empty.zip", [ArchiveMember("empty", b"")])
    backend = open_zip_backend(str(path))
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
        open_zip_backend(str(path))


def test_symlink_entry_is_rejected_even_with_one_file(tmp_path) -> None:
    path = write_zip(
        tmp_path / "special.zip",
        [
            ArchiveMember("data", b"payload"),
            ArchiveMember("link", kind="symlink", target="data"),
        ],
    )
    with pytest.raises(ArchiveStructureError, match="unsupported"):
        open_zip_backend(str(path))


def test_invalid_and_truncated_archives_are_open_failures(tmp_path) -> None:
    invalid = tmp_path / "invalid.zip"
    invalid.write_bytes(b"PK\x03\x04not-a-zip")
    with pytest.raises(InvalidArchiveError) as captured:
        open_zip_backend(str(invalid))
    assert isinstance(captured.value.__cause__, zipfile.BadZipFile)

    valid = write_zip(tmp_path / "valid.zip", [ArchiveMember("data", b"payload")])
    truncated = tmp_path / "truncated.zip"
    truncated.write_bytes(valid.read_bytes()[:-12])
    with pytest.raises(InvalidArchiveError):
        open_zip_backend(str(truncated))


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

    backend = open_zip_backend(str(path))
    with pytest.raises(ExtractionError) as captured:
        backend.read(100)
    assert isinstance(captured.value.__cause__, zipfile.BadZipFile)


def test_declared_size_limit_closes_backend(tmp_path) -> None:
    path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", b"payload")])
    backend = open_zip_backend(str(path))
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)


def test_early_close_is_idempotent(tmp_path) -> None:
    path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", b"payload")])
    backend = open_zip_backend(str(path))
    assert backend.read(1) == b"p"
    backend.close()
    backend.close()
    with pytest.raises(ValueError):
        backend.read(1)
