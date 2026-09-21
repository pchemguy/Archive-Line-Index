"""Tests for bounded, content-first path format classification."""

from __future__ import annotations

import builtins
import io
import tarfile

import pytest

from archive_line_index.formats import (
    DETECTION_PREFIX_SIZE,
    SourceFormat,
    detect_format,
)


def _write(tmp_path, name: str, content: bytes):
    path = tmp_path / name
    path.write_bytes(content)
    return path


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
    tmp_path, signature: bytes, expected: SourceFormat
) -> None:
    path = _write(tmp_path, "conflict.zip", signature + b"not-an-archive")
    assert detect_format(path) is expected


def test_valid_uncompressed_tar_header_is_detected(tmp_path) -> None:
    path = _write(tmp_path, "unconventional.data", _tar_bytes())
    assert detect_format(path) is SourceFormat.TAR


def test_ustar_text_without_a_valid_checksum_is_plain(tmp_path) -> None:
    content = bytearray(DETECTION_PREFIX_SIZE)
    content[257:262] = b"ustar"
    path = _write(tmp_path, "data", content)
    assert detect_format(path) is SourceFormat.PLAIN


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
    tmp_path, filename: str, expected: SourceFormat
) -> None:
    assert detect_format(_write(tmp_path, filename, b"not-an-archive")) is expected


@pytest.mark.parametrize("filename", ["payload", "payload.txt", "payload.gz"])
def test_unknown_or_plain_filename_falls_back_to_plain(tmp_path, filename) -> None:
    path = _write(tmp_path, filename, b"ordinary content")
    assert detect_format(path) is SourceFormat.PLAIN


def test_detection_requests_only_the_bounded_prefix(tmp_path, monkeypatch) -> None:
    path = _write(tmp_path, "large", b"x" * (DETECTION_PREFIX_SIZE * 4))
    requests = []
    original_open = builtins.open

    class RecordingReader:
        def __init__(self, stream) -> None:
            self._stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self._stream.close()

        def read(self, size=-1):
            requests.append(size)
            return self._stream.read(size)

    def recording_open(file, mode="r", *args, **kwargs):
        return RecordingReader(original_open(file, mode, *args, **kwargs))

    monkeypatch.setattr(builtins, "open", recording_open)
    assert detect_format(path) is SourceFormat.PLAIN
    assert requests == [DETECTION_PREFIX_SIZE]


def test_missing_path_preserves_filesystem_exception(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        detect_format(tmp_path / "missing")
