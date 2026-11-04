"""Real ZIP payloads compose with the unchanged public stream and scanner."""

import zipfile
from pathlib import Path

import pytest

from archive_line_index import (
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
    build_line_index,
    open_content_stream,
)


@pytest.mark.parametrize("name", ["payload.zip", "payload.unknown", "misleading.tar"])
@pytest.mark.parametrize("buffer_size", [1, 2, 7, 1024 * 1024])
def test_zip_signature_and_suffix_stream_exact_payload(
    tmp_path: Path, name: str, buffer_size: int
) -> None:
    payload = b"\xef\xbb\xbfalpha\r\n\nomega"
    plain = tmp_path / "plain"
    plain.write_bytes(payload)
    target = tmp_path / name
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nested/data.txt", payload)
    assert build_line_index(target, buffer_size=buffer_size).tolist() == [3, 10, 11, 16]
    assert build_line_index(target) == build_line_index(plain)
    with open_content_stream(target, max_uncompressed_size=len(payload)) as stream:
        assert stream.read(4) == payload[:4]
        buffer = bytearray(100)
        assert stream.readinto(buffer) == len(payload) - 4
        assert buffer[: len(payload) - 4] == payload[4:]
        assert stream.read() == b""
    with pytest.raises(SizeLimitExceededError):
        build_line_index(target, max_uncompressed_size=len(payload) - 1)


def test_claimed_invalid_zip_has_no_plain_fallback(tmp_path: Path) -> None:
    p = tmp_path / "not.zip"
    p.write_bytes(b"plain data\n")
    with pytest.raises(InvalidArchiveError):
        build_line_index(p)


def test_corrupt_zip_cannot_return_completed_index(tmp_path: Path) -> None:
    p = tmp_path / "bad.zip"
    with zipfile.ZipFile(p, "w") as archive:
        archive.writestr("data", b"a\nb\n")
    data = bytearray(p.read_bytes())
    data[34] ^= 1
    p.write_bytes(data)
    with pytest.raises(ExtractionError):
        build_line_index(p, buffer_size=1)
    p.unlink()
