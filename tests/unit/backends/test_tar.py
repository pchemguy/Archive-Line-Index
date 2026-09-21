"""Tests for validated sequential TAR member streaming."""

from __future__ import annotations

import io
import tarfile

import pytest

from archive_line_index.backends.tar import open_tar_backend
from archive_line_index.errors import (
    ArchiveStructureError,
    InvalidArchiveError,
    SizeLimitExceededError,
)
from archive_line_index.sources import open_source
from archive_line_index.stream import ContentStream
from tests.helpers.archive_factory import ArchiveMember, write_tar
from tests.helpers.streams import NonSeekableStream, ShortNonSeekableStream


def _read_backend(path_or_stream, size: int = 3) -> bytes:
    backend = open_tar_backend(open_source(path_or_stream))
    chunks = []
    try:
        while chunk := backend.read(size):
            chunks.append(chunk)
        assert backend.completed
        return b"".join(chunks)
    finally:
        backend.close()


@pytest.mark.parametrize(
    "filename",
    ["data.tar", "data.tar.gz", "data.tgz", "data.tar.bz2", "data.tbz2", "data.tar.xz", "data.txz"],
)
def test_tar_variants_stream_nested_member(tmp_path, filename: str) -> None:
    path = write_tar(
        tmp_path / filename,
        [
            ArchiveMember("nested", kind="directory"),
            ArchiveMember("nested/data.jsonl", b"a\nb"),
        ],
    )
    assert _read_backend(path, 1) == b"a\nb"


def test_caller_stream_remains_open(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tgz", [ArchiveMember("data", b"payload")])
    source = io.BytesIO(path.read_bytes())
    assert _read_backend(source) == b"payload"
    assert not source.closed


def test_empty_member_is_valid(tmp_path) -> None:
    path = write_tar(tmp_path / "empty.tar", [ArchiveMember("empty", b"")])
    backend = open_tar_backend(open_source(path))
    assert backend.declared_size == 0
    assert backend.read(1) == b""
    assert backend.completed
    backend.close()


def test_zero_regular_files_are_rejected_before_delivery(tmp_path) -> None:
    path = write_tar(
        tmp_path / "structure.tar",
        [ArchiveMember("directory", kind="directory")],
    )
    with pytest.raises(ArchiveStructureError, match="exactly one"):
        open_tar_backend(open_source(path))


@pytest.mark.parametrize(
    "members, expected",
    [
        ([ArchiveMember("a", b"a"), ArchiveMember("b", b"b")], b"a"),
        (
            [ArchiveMember("data", b"x"), ArchiveMember("__MACOSX/meta", b"m")],
            b"x",
        ),
    ],
)
def test_path_reports_late_additional_member(tmp_path, members, expected) -> None:
    path = write_tar(tmp_path / "structure.tar", members)
    backend = open_tar_backend(open_source(path))
    assert backend.read(64) == expected
    with pytest.raises(ArchiveStructureError, match="additional"):
        backend.read(64)


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo"])
def test_path_reports_late_special_member(tmp_path, kind: str) -> None:
    path = write_tar(
        tmp_path / "special.tar",
        [
            ArchiveMember("data", b"payload"),
            ArchiveMember("special", kind=kind, target="data"),
        ],
    )
    backend = open_tar_backend(open_source(path))
    assert backend.read(64) == b"payload"
    with pytest.raises(ArchiveStructureError, match="unsupported"):
        backend.read(64)


def test_streaming_backend_does_not_seek_caller_stream(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])

    class SeekCountingStream(io.BytesIO):
        def __init__(self, data: bytes) -> None:
            super().__init__(data)
            self.seek_calls = 0

        def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
            self.seek_calls += 1
            return super().seek(offset, whence)

    source = SeekCountingStream(path.read_bytes())
    assert _read_backend(source) == b"payload"
    assert source.seek_calls == 0


def test_invalid_archive_is_translated_with_cause(tmp_path) -> None:
    path = tmp_path / "invalid.tar"
    path.write_bytes(b"not-a-tar")
    with pytest.raises(InvalidArchiveError) as captured:
        open_tar_backend(open_source(path))
    assert isinstance(captured.value.__cause__, tarfile.TarError)


def test_truncated_compressed_archive_is_rejected(tmp_path) -> None:
    valid = write_tar(
        tmp_path / "valid.tgz",
        [ArchiveMember("data", b"payload" * 1000)],
    )
    truncated = tmp_path / "truncated.tgz"
    content = valid.read_bytes()
    truncated.write_bytes(content[: len(content) // 2])
    with pytest.raises(InvalidArchiveError):
        open_tar_backend(open_source(truncated))


def test_declared_size_limit_rejects_and_preserves_caller(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    source = io.BytesIO(path.read_bytes())
    backend = open_tar_backend(open_source(source))
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)
    assert not source.closed


def test_early_close_is_idempotent_and_preserves_caller(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    source = io.BytesIO(path.read_bytes())
    backend = open_tar_backend(open_source(source))
    assert backend.read(1) == b"p"
    backend.close()
    backend.close()
    assert not source.closed
    with pytest.raises(ValueError):
        backend.read(1)


def test_nonseekable_tar_streams_and_validates_terminal_eof(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    source = NonSeekableStream(path.read_bytes())
    backend = open_tar_backend(open_source(source))
    assert backend.read(64) == b"payload"
    assert not backend.completed
    assert backend.read(64) == b""
    assert backend.completed
    backend.close()
    assert not source.closed


@pytest.mark.parametrize("max_chunk", [1, 7, 511])
def test_nonseekable_tar_accepts_arbitrary_short_source_reads(
    tmp_path, max_chunk: int
) -> None:
    path = write_tar(tmp_path / "data.tgz", [ArchiveMember("data", b"payload")])
    source = ShortNonSeekableStream(path.read_bytes(), max_chunk=max_chunk)
    assert _read_backend(source, 2) == b"payload"
    assert not source.closed


def test_nonseekable_tar_reports_late_additional_member(tmp_path) -> None:
    path = write_tar(
        tmp_path / "multiple.tar",
        [ArchiveMember("first", b"prefix"), ArchiveMember("later", b"x")],
    )
    source = NonSeekableStream(path.read_bytes())
    backend = open_tar_backend(open_source(source))
    assert backend.read(64) == b"prefix"
    with pytest.raises(ArchiveStructureError, match="additional"):
        backend.read(64)
    assert not source.closed


def test_nonseekable_tar_reports_late_special_member(tmp_path) -> None:
    path = write_tar(
        tmp_path / "special.tar",
        [
            ArchiveMember("first", b"prefix"),
            ArchiveMember("later", kind="symlink", target="first"),
        ],
    )
    backend = open_tar_backend(open_source(NonSeekableStream(path.read_bytes())))
    assert backend.read(64) == b"prefix"
    with pytest.raises(ArchiveStructureError, match="unsupported"):
        backend.read(64)


def test_nonseekable_early_close_does_not_validate_trailing_members(tmp_path) -> None:
    path = write_tar(
        tmp_path / "multiple.tar",
        [ArchiveMember("first", b"prefix"), ArchiveMember("later", b"x")],
    )
    source = NonSeekableStream(path.read_bytes())
    backend = open_tar_backend(open_source(source))
    assert backend.read(1) == b"p"
    backend.close()
    assert not source.closed


def test_streaming_tar_creates_no_extraction_artifacts(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    before = {item.name for item in tmp_path.iterdir()}
    assert _read_backend(NonSeekableStream(path.read_bytes())) == b"payload"
    assert {item.name for item in tmp_path.iterdir()} == before
