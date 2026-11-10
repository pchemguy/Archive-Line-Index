"""Generated content demonstrates bounded scanning independent of line length."""

import tracemalloc
from pathlib import Path
from typing import BinaryIO
from unittest.mock import patch

import pytest

from archive_stream.scanner import scan_line_offsets


def test_long_line_storage_does_not_grow_with_payload() -> None:
    class Generated:
        remaining = 32 * 1024 * 1024
        requests = 0

        def read(self, size: int = -1, /) -> bytes:
            assert 0 < size <= 8192
            self.requests += 1
            count = min(size, self.remaining)
            self.remaining -= count
            return b"x" * count

    source = Generated()
    tracemalloc.start()
    try:
        offsets = scan_line_offsets(source, buffer_size=8192)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert offsets.tolist() == [0, 32 * 1024 * 1024]
    assert source.requests > 4000
    assert peak < 128 * 1024


@pytest.mark.parametrize(
    "default_buffer", [8192, 131072], ids=["8k-default", "128k-default"]
)
def test_plain_stream_delivers_incrementally_with_bounded_storage(
    tmp_path: Path,
    default_buffer: int,
) -> None:
    from archive_stream import open_content_stream

    path = tmp_path / "large.bin"
    with path.open("wb") as output:
        for _ in range(1024):
            output.write(b"x" * 8192)
    real_open = Path.open

    def opened(path: Path, mode: str = "r", buffering: int = -1) -> BinaryIO:
        assert mode == "rb"
        return real_open(
            path, "rb", buffering=default_buffer if buffering < 0 else buffering
        )

    tracemalloc.start()
    try:
        with (
            patch.object(Path, "open", new=opened),
            open_content_stream(path) as stream,
        ):
            assert stream.read(3) == b"xxx"
            total = 3
            while block := stream.read(8192):
                assert block == b"x" * len(block)
                total += len(block)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert total == 8 * 1024 * 1024 and stream.closed
    assert peak < 128 * 1024
