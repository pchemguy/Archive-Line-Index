"""Tests for the plain-path backend."""

from __future__ import annotations

from pathlib import Path

import pytest

from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.plain import open_plain_backend


def _read_all(reader: BackendReader, size: int = 3) -> bytes:
    chunks = []
    while chunk := reader.read(size):
        chunks.append(chunk)
    return b"".join(chunks)


@pytest.mark.parametrize("content", [b"", b"payload", b"x" * (2 * 1024 * 1024)])
def test_plain_backend_reads_empty_and_large_paths(tmp_path, content: bytes) -> None:
    path = tmp_path / "payload"
    path.write_bytes(content)
    reader = open_plain_backend(str(path))

    assert isinstance(reader, BackendReader)
    assert reader.declared_size == len(content)
    assert _read_all(reader, 65_537) == content
    assert reader.completed
    assert reader.read(1) == b""


def test_early_close_is_idempotent_and_closes_owned_file(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"payload")
    reader = open_plain_backend(str(path))
    raw = reader._stream
    assert reader.read(2) == b"pa"

    reader.close()
    reader.close()

    assert raw.closed
    with pytest.raises(ValueError, match="closed backend"):
        reader.read(1)


def test_missing_path_preserves_filesystem_exception(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        open_plain_backend(str(tmp_path / "missing"))


@pytest.mark.parametrize("size", [0, -1, True, 1.5])
def test_backend_requires_positive_integer_read_sizes(tmp_path, size) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"data")
    reader = open_plain_backend(str(path))
    with pytest.raises((TypeError, ValueError)):
        reader.read(size)
    reader.close()
