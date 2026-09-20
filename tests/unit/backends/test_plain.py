"""Tests for the plain-source backend."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.plain import open_plain_backend
from archive_line_index.sources import open_source


class ShortReadStream(io.BytesIO):
    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = 2
        return super().read(min(size, 2))


class FailingStream(io.BytesIO):
    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b""
        raise OSError("read failed")


class NonSeekableStream(ShortReadStream):
    def seekable(self) -> bool:
        return False


def _read_all(reader: BackendReader, size: int = 3) -> bytes:
    chunks = []
    while chunk := reader.read(size):
        chunks.append(chunk)
    return b"".join(chunks)


@pytest.mark.parametrize("content", [b"", b"payload", b"x" * (2 * 1024 * 1024)])
def test_plain_backend_reads_empty_and_large_seekable_sources(content: bytes) -> None:
    reader = open_plain_backend(open_source(io.BytesIO(content)))

    assert isinstance(reader, BackendReader)
    assert reader.declared_size == len(content)
    assert _read_all(reader, 65_537) == content
    assert reader.completed
    assert reader.read(1) == b""


def test_arbitrary_source_short_reads_are_preserved() -> None:
    reader = open_plain_backend(open_source(ShortReadStream(b"abcdef")))
    assert [reader.read(5), reader.read(5), reader.read(5), reader.read(5)] == [
        b"ab",
        b"cd",
        b"ef",
        b"",
    ]
    assert reader.completed


def test_nonseekable_detection_prefix_is_replayed() -> None:
    handle = open_source(NonSeekableStream(b"abcdef"))
    assert handle.probe_prefix(4) == b"abcd"

    reader = open_plain_backend(handle)
    assert reader.declared_size is None
    assert _read_all(reader, 3) == b"abcdef"


def test_read_failure_propagates_without_false_completion() -> None:
    reader = open_plain_backend(open_source(FailingStream()))
    with pytest.raises(OSError, match="read failed"):
        reader.read(4)
    assert not reader.completed


def test_early_close_preserves_caller_owned_source() -> None:
    stream = io.BytesIO(b"payload")
    reader = open_plain_backend(open_source(stream))
    assert reader.read(2) == b"pa"

    reader.close()
    reader.close()

    assert not stream.closed
    with pytest.raises(ValueError, match="closed backend"):
        reader.read(1)


def test_close_releases_path_owned_source(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"payload")
    handle = open_source(path)
    raw = handle._stream
    reader = open_plain_backend(handle)

    reader.close()

    assert raw.closed


@pytest.mark.parametrize("size", [0, -1, True, 1.5])
def test_backend_requires_positive_integer_read_sizes(size) -> None:
    reader = open_plain_backend(open_source(io.BytesIO(b"data")))
    with pytest.raises((TypeError, ValueError)):
        reader.read(size)
