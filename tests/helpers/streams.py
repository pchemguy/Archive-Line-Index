"""Controlled binary streams for boundary, failure, and ownership tests."""

from __future__ import annotations

import io


class ShortReadStream(io.BytesIO):
    def __init__(self, content: bytes, *, max_chunk: int) -> None:
        super().__init__(content)
        self.max_chunk = max_chunk
        self.requests: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.requests.append(size)
        if size < 0:
            size = self.max_chunk
        return super().read(min(size, self.max_chunk))


class FailingReadStream(io.BytesIO):
    def __init__(self, content: bytes, *, fail_after_reads: int) -> None:
        super().__init__(content)
        self.fail_after_reads = fail_after_reads
        self.read_count = 0

    def read(self, size: int = -1) -> bytes:
        self.read_count += 1
        if self.read_count > self.fail_after_reads:
            raise OSError("controlled read failure")
        return super().read(size)
