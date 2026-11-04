"""Detection is bounded classification, not archive parsing."""

import io
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.formats import FormatKind, detect_format


@pytest.mark.parametrize(
    "name,kind",
    [
        ("a.ZIP", "zip"),
        ("a.7Z", "7z"),
        ("a.TAR.GZ", "tar"),
        ("a.tgz", "tar"),
        ("a.tar.bz2", "tar"),
        ("a.TBZ", "tar"),
        ("a.tbz2", "tar"),
        ("a.tar.xz", "tar"),
        ("a.txz", "tar"),
        ("a.unknown", "plain"),
    ],
)
def test_suffix_candidates(tmp_path: Path, name: str, kind: str) -> None:
    p = tmp_path / name
    p.write_bytes(b"not an archive")
    c = detect_format(p)
    assert c.kind.value == kind
    assert c.signature_kind is None
    assert c.suffix_kind is (None if kind == "plain" else c.kind)


@pytest.mark.parametrize(
    "prefix,kind",
    [
        (b"7z\xbc\xaf\x27\x1c", "7z"),
        (b"PK\x03\x04", "zip"),
        (b"PK\x05\x06", "zip"),
        (b"PK\x07\x08", "zip"),
        (b"\x1f\x8b", "tar"),
        (b"BZh", "tar"),
        (b"\xfd7zXZ\x00", "tar"),
    ],
)
def test_signature_wins(tmp_path: Path, prefix: bytes, kind: str) -> None:
    p = tmp_path / "wrong.zip"
    p.write_bytes(prefix)
    c = detect_format(p)
    assert c.kind.value == kind
    assert c.signature_kind == c.kind
    assert c.suffix_kind == FormatKind.ZIP


def test_tar_checksum_and_zero_prefix(tmp_path: Path) -> None:
    p = tmp_path / "unknown"
    header = tarfile.TarInfo("payload").tobuf()
    p.write_bytes(header)
    assert detect_format(p).kind == FormatKind.TAR
    p.write_bytes(b"\0" * 512)
    assert detect_format(p).kind == FormatKind.PLAIN
    p.write_bytes(b"X" + header[1:])
    assert detect_format(p).kind == FormatKind.PLAIN


def test_inspection_reads_at_most_512_bytes(tmp_path: Path) -> None:
    class Probe(io.BytesIO):
        def read(self, size: int = -1, /) -> bytes:
            assert 0 < size <= 512
            return super().read(size)

    with patch.object(Path, "open", return_value=Probe(b"x" * 4096)) as opened:
        assert detect_format(tmp_path / "x").kind == FormatKind.PLAIN
        opened.assert_called_once()


@pytest.mark.parametrize("chunk", [1, 17, 512])
def test_detection_limits_raw_reads_and_handles_short_reads(
    tmp_path: Path, chunk: int
) -> None:
    class Raw(io.RawIOBase):
        def __init__(self) -> None:
            self.payload = tarfile.TarInfo("payload").tobuf() + b"x" * 4096
            self.position = 0
            self.requests: list[int] = []

        def readable(self) -> bool:
            return True

        def readinto(self, buffer: bytearray) -> int:
            self.requests.append(len(buffer))
            count = min(chunk, len(buffer), len(self.payload) - self.position)
            buffer[:count] = self.payload[self.position : self.position + count]
            self.position += count
            return count

    raw = Raw()

    def opened(
        path: Path, mode: str = "r", buffering: int = -1
    ) -> io.RawIOBase | io.BufferedReader:
        assert mode == "rb"
        if buffering == 0:
            return raw
        return io.BufferedReader(
            raw, buffer_size=131072 if buffering < 0 else buffering
        )

    with patch.object(Path, "open", new=opened):
        candidate = detect_format(tmp_path / "unconventional.bin")
    assert candidate.signature_kind == FormatKind.TAR
    assert raw.position == 512
    assert all(0 < count <= 512 for count in raw.requests)
    assert raw.closed
