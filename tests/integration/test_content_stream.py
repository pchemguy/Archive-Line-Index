"""Actual plain adapter/common-stream milestone demonstration."""

from pathlib import Path

import pytest

from archive_line_index.backends.registry import open_backend
from archive_line_index.errors import SizeLimitExceededError
from archive_line_index.formats import detect_format
from archive_line_index.stream import make_content_stream


@pytest.mark.parametrize("size", [0, 1, 17, 131073])
def test_plain_bytes_across_delivery_shapes(tmp_path: Path, size: int) -> None:
    payload = (bytes(range(256)) * ((size + 255) // 256))[:size]
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)
    reader = open_backend(path, detect_format(path))
    with make_content_stream(reader, max_uncompressed_size=size) as stream:
        first = stream.read(3)
        target = bytearray(b"?" * 19)
        count = stream.readinto(target)
        assert target[count:] == b"?" * (19 - count)
        assert first + target[:count] + stream.read() == payload
        assert stream.read(1) == b""
    assert stream.closed
    path.unlink()


def test_plain_declared_limit_releases_file(tmp_path: Path) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"abc")
    reader = open_backend(path, detect_format(path))
    with pytest.raises(SizeLimitExceededError):
        make_content_stream(reader, max_uncompressed_size=2)
    with pytest.raises(ValueError):
        reader.read(1)
