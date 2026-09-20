"""Tests for bounded, content-first format classification."""

from __future__ import annotations

import io
import tarfile

import pytest

from archive_line_index.formats import (
    DETECTION_PREFIX_SIZE,
    SourceFormat,
    detect_format,
)
from archive_line_index.sources import open_source


def _tar_bytes() -> bytes:
    destination = io.BytesIO()
    with tarfile.open(fileobj=destination, mode="w") as archive:
        info = tarfile.TarInfo("payload.txt")
        data = b"payload"
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    return destination.getvalue()


@pytest.mark.parametrize(
    ("signature", "expected"),
    [
        (b"7z\xbc\xaf\x27\x1c", SourceFormat.SEVEN_ZIP),
        (b"PK\x03\x04", SourceFormat.ZIP),
        (b"PK\x05\x06", SourceFormat.ZIP),
        (b"PK\x07\x08", SourceFormat.ZIP),
        (b"\x1f\x8b", SourceFormat.TAR),
        (b"BZh", SourceFormat.TAR),
        (b"\xfd7zXZ\x00", SourceFormat.TAR),
    ],
)
def test_recognized_signature_wins_over_conflicting_suffix(
    signature: bytes, expected: SourceFormat
) -> None:
    handle = open_source(io.BytesIO(signature + b"not-an-archive"))
    assert detect_format(handle, filename="conflict.zip") is expected


def test_valid_uncompressed_tar_header_is_detected() -> None:
    handle = open_source(io.BytesIO(_tar_bytes()))
    assert detect_format(handle, filename="unconventional.data") is SourceFormat.TAR


def test_ustar_text_without_a_valid_checksum_is_plain() -> None:
    content = bytearray(DETECTION_PREFIX_SIZE)
    content[257:262] = b"ustar"
    handle = open_source(io.BytesIO(content))
    assert detect_format(handle) is SourceFormat.PLAIN


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("archive.ZIP", SourceFormat.ZIP),
        ("archive.7Z", SourceFormat.SEVEN_ZIP),
        ("archive.TAR", SourceFormat.TAR),
        ("archive.TAR.GZ", SourceFormat.TAR),
        ("archive.TGZ", SourceFormat.TAR),
        ("archive.TAR.BZ2", SourceFormat.TAR),
        ("archive.TBZ2", SourceFormat.TAR),
        ("archive.TBZ", SourceFormat.TAR),
        ("archive.TAR.XZ", SourceFormat.TAR),
        ("archive.TXZ", SourceFormat.TAR),
    ],
)
def test_recognized_suffix_claims_a_candidate(
    filename: str, expected: SourceFormat
) -> None:
    handle = open_source(io.BytesIO(b"not-an-archive"))
    assert detect_format(handle, filename=filename) is expected


@pytest.mark.parametrize("filename", [None, "payload", "payload.txt", "payload.gz"])
def test_unknown_or_plain_filename_falls_back_to_plain(filename) -> None:
    handle = open_source(io.BytesIO(b"ordinary content"))
    assert detect_format(handle, filename=filename) is SourceFormat.PLAIN


def test_nonseekable_detection_prefix_is_replayed_exactly() -> None:
    class NonSeekable(io.BytesIO):
        def seekable(self) -> bool:
            return False

    content = b"plain nonseekable payload"
    handle = open_source(NonSeekable(content))
    assert detect_format(handle) is SourceFormat.PLAIN
    assert handle.read() == content


def test_seekable_detection_restores_attachment_origin() -> None:
    stream = io.BytesIO(b"prefix" + b"PK\x03\x04payload")
    stream.seek(len(b"prefix"))
    handle = open_source(stream)

    assert detect_format(handle) is SourceFormat.ZIP
    assert handle.tell() == 0
    assert handle.read(4) == b"PK\x03\x04"


def test_detection_requests_only_the_bounded_prefix() -> None:
    class RecordingStream(io.BytesIO):
        def __init__(self, data: bytes) -> None:
            super().__init__(data)
            self.requests: list[int] = []

        def read(self, size: int = -1) -> bytes:
            self.requests.append(size)
            return super().read(size)

    stream = RecordingStream(b"x" * (DETECTION_PREFIX_SIZE * 4))
    handle = open_source(stream)
    assert detect_format(handle) is SourceFormat.PLAIN
    assert max(stream.requests) == DETECTION_PREFIX_SIZE
    assert stream.tell() == 0


def test_bytes_filename_is_rejected_after_prefix_restoration() -> None:
    class BytesPath:
        def __fspath__(self) -> bytes:
            return b"invalid.zip"

    handle = open_source(io.BytesIO(b"plain"))
    with pytest.raises(TypeError, match="resolve to str"):
        detect_format(handle, filename=BytesPath())
