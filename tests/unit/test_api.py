"""Facade validation, source composition and owned versus borrowed inputs."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.helpers.readers import Reader

import archive_line_index as ali
from archive_line_index.api import build_line_index, open_content_stream


@pytest.mark.parametrize(
    "payload", [b"", b"\xef\xbb\xbf", b"a\r\n\nb", bytes(range(256))]
)
def test_source_and_direct_scanning_agree(tmp_path: Path, payload: bytes) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)
    with open_content_stream(path) as source:
        assert source.read() == payload
    assert source.closed
    for skip in (True, False):
        borrowed = io.BytesIO(payload)
        direct = ali.scan_line_offsets(borrowed, skip_utf8_bom=skip, buffer_size=2)
        assert build_line_index(str(path), skip_utf8_bom=skip, buffer_size=1) == direct
        assert not borrowed.closed


@pytest.mark.parametrize(
    "options,exc",
    [
        ({"buffer_size": True}, TypeError),
        ({"buffer_size": 0}, ValueError),
        ({"skip_utf8_bom": 1}, TypeError),
        ({"max_uncompressed_size": True}, TypeError),
        ({"max_uncompressed_size": -1}, ValueError),
    ],
)
def test_build_validates_before_source_open(
    options: dict[str, object], exc: type[Exception]
) -> None:
    with (
        patch.object(Path, "open", side_effect=AssertionError("avoid IO")),
        pytest.raises(exc),
    ):
        build_line_index("missing", **options)  # type: ignore[arg-type]


@pytest.mark.parametrize("source", [b"path", object(), 42])
def test_invalid_source_before_io(source: object) -> None:
    with (
        patch.object(Path, "open", side_effect=AssertionError("avoid IO")),
        pytest.raises(TypeError),
    ):
        open_content_stream(source)  # type: ignore[arg-type]


def test_open_limit_validated_before_detection() -> None:
    with (
        patch.object(Path, "open", side_effect=AssertionError("avoid IO")),
        pytest.raises(TypeError),
    ):
        open_content_stream("missing", max_uncompressed_size=True)


def test_build_closes_reader_after_scanner_failure(tmp_path: Path) -> None:
    path = tmp_path / "p"
    path.write_bytes(b"plain")
    error = MemoryError("index allocation")
    r = Reader(b"data")
    with (
        patch("archive_line_index.api.open_backend", return_value=r),
        patch("archive_line_index.api.scan_line_offsets", side_effect=error),
    ):
        with pytest.raises(MemoryError) as caught:
            build_line_index(path)
    assert caught.value is error and r.closes == 1


def test_successful_scan_does_not_hide_close_failure(tmp_path: Path) -> None:
    path = tmp_path / "p"
    path.write_bytes(b"plain")
    r = Reader(b"data", close_failures=1)
    with (
        patch("archive_line_index.api.open_backend", return_value=r),
        pytest.raises(OSError, match="close fault"),
    ):
        build_line_index(path)
    assert r.closes == 1
    r.close()


def test_filesystem_and_undelivered_archive_failures(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_line_index(tmp_path / "missing")
    path = tmp_path / "claimed.zip"
    path.write_bytes(b"invalid claimed archive")
    with pytest.raises(ali.UnsupportedFormatError):
        build_line_index(path)
