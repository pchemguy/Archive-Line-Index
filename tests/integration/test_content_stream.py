"""Integration tests for opening plain content streams."""

from __future__ import annotations

import io
import zipfile

import pytest

from archive_line_index import (
    ContentStream,
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
    open_content_stream,
)
from tests.helpers.archive_factory import ArchiveMember, write_7z, write_tar, write_zip


def test_path_source_streams_bytes_and_closes_with_context(tmp_path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_bytes(b"first\nsecond")

    with open_content_stream(path) as stream:
        assert isinstance(stream, ContentStream)
        assert stream.read(3) == b"fir"
        assert stream.read() == b"st\nsecond"

    assert stream.closed


def test_non_path_source_is_rejected_before_reading() -> None:
    source = io.BytesIO(b"payload")

    with pytest.raises(TypeError, match="filesystem path"):
        open_content_stream(source)

    assert source.read() == b"payload"
    assert not source.closed


def test_exact_maximum_size_is_allowed(tmp_path) -> None:
    source = tmp_path / "payload"
    source.write_bytes(b"payload")
    with open_content_stream(source, max_uncompressed_size=7) as stream:
        assert stream.read() == b"payload"


def test_size_limit_failure_closes_package_source(tmp_path) -> None:
    source = tmp_path / "payload"
    source.write_bytes(b"payload")
    with pytest.raises(SizeLimitExceededError, match="declared"):
        open_content_stream(source, max_uncompressed_size=6)


@pytest.mark.parametrize("limit", [True, -1, 1.5, "7"])
def test_invalid_size_limit_fails_before_path_open(tmp_path, limit) -> None:
    missing = tmp_path / "missing.jsonl"
    with pytest.raises((TypeError, ValueError)):
        open_content_stream(missing, max_uncompressed_size=limit)


@pytest.mark.parametrize(
    "signature",
    [b"PK\x03\x04", b"7z\xbc\xaf\x27\x1c", b"\x1f\x8b"],
)
def test_signature_claimed_invalid_archives_never_fall_back_to_plain(
    tmp_path, signature: bytes,
) -> None:
    source = tmp_path / "source"
    source.write_bytes(signature + b"not-an-archive")
    with pytest.raises(InvalidArchiveError):
        open_content_stream(source)


@pytest.mark.parametrize("read_size", [1, 3, 64])
def test_zip_and_plain_streams_are_byte_identical(tmp_path, read_size: int) -> None:
    content = b"\xef\xbb\xbfalpha\r\n\nbeta"
    plain = tmp_path / "data.jsonl"
    plain.write_bytes(content)
    zipped = write_zip(
        tmp_path / "data.zip",
        [ArchiveMember("nested/data.jsonl", content)],
    )

    def consume(path) -> bytes:
        chunks = []
        with open_content_stream(path) as stream:
            while chunk := stream.read(read_size):
                chunks.append(chunk)
        return b"".join(chunks)

    assert consume(zipped) == consume(plain) == content


def test_zip_crc_failure_is_raised_through_public_stream(tmp_path) -> None:
    path = tmp_path / "crc.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("data", b"payload")
    content = bytearray(path.read_bytes())
    local = content.index(b"PK\x03\x04")
    name_length = int.from_bytes(content[local + 26 : local + 28], "little")
    extra_length = int.from_bytes(content[local + 28 : local + 30], "little")
    content[local + 30 + name_length + extra_length] ^= 0xFF
    path.write_bytes(content)

    with open_content_stream(path) as stream:
        with pytest.raises(ExtractionError):
            stream.read()


@pytest.mark.parametrize(
    "filename",
    ["data.tar", "data.tgz", "data.tbz2", "data.txz"],
)
@pytest.mark.parametrize("read_size", [1, 64])
def test_tar_variants_and_plain_are_byte_identical(
    tmp_path, filename: str, read_size: int
) -> None:
    content = b"\xef\xbb\xbfalpha\r\n\nbeta"
    archived = write_tar(
        tmp_path / filename,
        [ArchiveMember("nested/data.jsonl", content)],
    )
    with open_content_stream(archived) as stream:
        chunks = []
        while chunk := stream.read(read_size):
            chunks.append(chunk)
    assert b"".join(chunks) == content


@pytest.mark.parametrize("filename", ["broken.tar", "broken.tgz", "broken.tbz2", "broken.txz"])
def test_misleading_tar_suffix_is_never_plain_fallback(tmp_path, filename: str) -> None:
    path = tmp_path / filename
    path.write_bytes(b"ordinary bytes")
    with pytest.raises(InvalidArchiveError):
        open_content_stream(path)


@pytest.mark.parametrize("read_size", [1, 3, 64])
def test_sevenzip_and_plain_streams_are_byte_identical(
    tmp_path, read_size: int
) -> None:
    content = b"\xef\xbb\xbfalpha\r\n\nbeta"
    archived = write_7z(
        tmp_path / "data.7z",
        [ArchiveMember("nested/data.jsonl", content)],
    )
    chunks = []
    with open_content_stream(archived) as stream:
        while chunk := stream.read(read_size):
            chunks.append(chunk)
    assert b"".join(chunks) == content


def test_misleading_sevenzip_suffix_is_never_plain_fallback(tmp_path) -> None:
    path = tmp_path / "broken.7z"
    path.write_bytes(b"ordinary bytes")
    with pytest.raises(InvalidArchiveError):
        open_content_stream(path)
