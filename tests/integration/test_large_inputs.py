"""Generated content demonstrates bounded scanning independent of line length."""

import tracemalloc

from archive_line_index.scanner import scan_line_offsets


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
