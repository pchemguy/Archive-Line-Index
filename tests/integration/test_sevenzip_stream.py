"""7z public streams retain exact bytes, common limits and worker ownership."""

import threading
from pathlib import Path
from unittest.mock import patch

import py7zr
import pytest
from tests.helpers.sevenzip import make_7z

from archive_line_index import (
    ExtractionError,
    SizeLimitExceededError,
    open_content_stream,
)


def owned_threads() -> set[threading.Thread]:
    return {t for t in threading.enumerate() if t.name == "ali-7z-extract"}


@pytest.mark.parametrize("name", ["source.7z", "source.zip", "source.unknown"])
@pytest.mark.parametrize("payload", [b"", b"\xef\xbb\xbfalpha\r\n\nomega"])
def test_7z_public_stream_bytes_limits_and_cleanup(
    tmp_path: Path, name: str, payload: bytes
) -> None:
    target = make_7z(tmp_path / name, [("nested/data", payload)])
    before = owned_threads()
    with open_content_stream(target, max_uncompressed_size=len(payload)) as stream:
        assert stream.read(0) == b""
        assert stream.read(2) == payload[:2]
        buffer = bytearray(b"?" * 100)
        count = stream.readinto(buffer)
        assert count == max(0, len(payload) - 2)
        assert buffer[:count] == payload[2:]
        assert buffer[count:] == b"?" * (100 - count)
        assert stream.read() == b""
    assert owned_threads() == before
    if payload:
        with pytest.raises(SizeLimitExceededError):
            open_content_stream(target, max_uncompressed_size=len(payload) - 1)
        assert owned_threads() == before


def test_7z_actual_size_limit_does_not_trust_metadata(tmp_path: Path) -> None:
    target = make_7z(tmp_path / "source.7z", [("data", b"abcdefgh")])
    original = py7zr.SevenZipFile.list

    def understated(archive: py7zr.SevenZipFile) -> list[py7zr.FileInfo]:
        info = original(archive)
        info[0].uncompressed = 1
        return info

    before = owned_threads()
    with patch.object(py7zr.SevenZipFile, "list", understated):
        stream = open_content_stream(target, max_uncompressed_size=3)
        try:
            assert stream.read(2) == b"ab"
            buffer = bytearray(b"????")
            with pytest.raises(SizeLimitExceededError):
                stream.readinto(buffer)
            assert buffer == b"????"
        finally:
            stream.close()
    assert owned_threads() == before


def test_real_7z_crc_failure_retained_and_worker_released(tmp_path: Path) -> None:
    target = make_7z(
        tmp_path / "bad.7z", [("data", b"a\nb\n")], filters=[{"id": py7zr.FILTER_COPY}]
    )
    raw = bytearray(target.read_bytes())
    raw[32] ^= 1
    target.write_bytes(raw)
    before = owned_threads()
    stream = open_content_stream(target)
    try:
        with pytest.raises(ExtractionError) as first:
            stream.read()
        assert first.value.__cause__ is not None
        with pytest.raises(ExtractionError) as second:
            stream.read(1)
        assert second.value is first.value
    finally:
        stream.close()
    assert owned_threads() == before
    target.unlink()


def test_failed_7z_worker_start_releases_archive_and_source(tmp_path: Path) -> None:
    target = make_7z(tmp_path / "source.7z", [("data", b"x")])
    inspection = target.open("rb")
    source = target.open("rb")
    with (
        patch.object(Path, "open", side_effect=[inspection, source]),
        patch(
            "archive_line_index.backends.sevenzip.start_queue_reader",
            side_effect=RuntimeError("startup"),
        ),
    ):
        with pytest.raises(ExtractionError) as error:
            open_content_stream(target)
    assert isinstance(error.value.__cause__, RuntimeError)
    assert source.closed


@pytest.mark.parametrize("corrupt", [False, True])
def test_7z_cleanup_failure_preserves_primary_and_remains_retryable(
    tmp_path: Path, corrupt: bool
) -> None:
    target = make_7z(
        tmp_path / "source.7z",
        [("data", b"payload\n")],
        filters=[{"id": py7zr.FILTER_COPY}],
    )
    if corrupt:
        raw = bytearray(target.read_bytes())
        raw[32] ^= 1
        target.write_bytes(raw)
    before = owned_threads()
    with patch.object(
        py7zr.SevenZipFile, "close", side_effect=OSError("archive cleanup")
    ):
        stream = open_content_stream(target)
        backend = stream._reader
        source = backend._owner.source
        error_type = ExtractionError if corrupt else OSError
        with pytest.raises(error_type) as error:
            stream.read()
        assert source.closed and not backend._reader._thread.is_alive()
        assert not stream.closed
        assert getattr(error.value, "__notes__", [])
        with pytest.raises(OSError, match="archive cleanup"):
            stream.close()
    stream.close()
    assert stream.closed and backend._owner.archive is None
    assert owned_threads() == before
