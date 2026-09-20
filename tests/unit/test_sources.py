"""Tests for source normalization, ownership, and prefix replay."""

from __future__ import annotations

import builtins
import io
from pathlib import Path

import pytest

from archive_line_index.sources import SourceHandle, open_source


class NonSeekableBytes(io.BytesIO):
    def seekable(self) -> bool:
        return False

    def seek(self, *args, **kwargs):
        raise io.UnsupportedOperation("not seekable")

    def tell(self) -> int:
        raise io.UnsupportedOperation("not seekable")


class ShortReadBytes(NonSeekableBytes):
    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = 1
        return super().read(min(size, 1))


class BecomesTextStream:
    def read(self, size: int = -1):
        return b"" if size == 0 else "text"

    def seekable(self) -> bool:
        return False


@pytest.mark.parametrize("as_path", [False, True])
def test_string_and_pathlike_sources_are_owned(
    tmp_path: Path, as_path: bool
) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"payload")
    source = path if as_path else str(path)

    handle = open_source(source)
    raw = handle._stream
    assert handle.owned
    assert handle.read() == b"payload"

    handle.close()
    assert raw.closed


def test_missing_path_preserves_filesystem_exception(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        open_source(tmp_path / "missing.bin")


def test_inaccessible_path_preserves_permission_error(monkeypatch) -> None:
    def denied(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(builtins, "open", denied)
    with pytest.raises(PermissionError, match="denied"):
        open_source("payload.bin")


def test_bytes_pathlike_is_rejected() -> None:
    class BytesPath:
        def __fspath__(self) -> bytes:
            return b"payload.bin"

    with pytest.raises(TypeError, match="resolve to str"):
        open_source(BytesPath())


def test_seekable_source_origin_and_probe_are_relative() -> None:
    source = io.BytesIO(b"ignored:payload")
    source.seek(len(b"ignored:"))
    handle = open_source(source)

    assert handle.tell() == 0
    assert handle.probe_prefix(4) == b"payl"
    assert handle.tell() == 0
    assert handle.read(3) == b"pay"
    assert handle.tell() == 3
    assert source.tell() == len(b"ignored:") + 3


def test_nonseekable_short_read_prefix_is_fully_probed_and_replayed() -> None:
    source = ShortReadBytes(b"abcdef")
    handle = open_source(source)

    assert not handle.seekable()
    assert handle.probe_prefix(4) == b"abcd"
    assert handle.read(2) == b"ab"
    assert handle.read(3) == b"cde"
    assert handle.read(3) == b"f"
    assert handle.read(3) == b""


def test_nonseekable_positioning_is_unsupported() -> None:
    handle = open_source(NonSeekableBytes(b"data"))
    with pytest.raises(io.UnsupportedOperation):
        handle.tell()
    with pytest.raises(io.UnsupportedOperation):
        handle.seek(0)


def test_text_stream_is_rejected_without_consumption() -> None:
    source = io.StringIO("text")
    with pytest.raises(TypeError, match="must return bytes"):
        open_source(source)
    assert source.tell() == 0
    assert not source.closed


def test_later_nonbinary_read_is_rejected() -> None:
    handle = open_source(BecomesTextStream())
    with pytest.raises(TypeError, match="must return bytes"):
        handle.read(1)


def test_caller_owned_source_is_not_closed_and_release_is_idempotent() -> None:
    source = io.BytesIO(b"data")
    handle = open_source(source)

    assert not handle.owned
    handle.release()
    handle.release()

    assert handle.closed
    assert not source.closed
    with pytest.raises(ValueError, match="closed source"):
        handle.read(1)


def test_prefix_can_only_be_probed_once() -> None:
    handle = SourceHandle(io.BytesIO(b"data"), owned=False)
    assert handle.probe_prefix(2) == b"da"
    with pytest.raises(RuntimeError, match="already been probed"):
        handle.probe_prefix(2)
