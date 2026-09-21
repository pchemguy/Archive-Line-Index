"""Backend-independent read-only sequential content stream."""

from __future__ import annotations

import io
import operator

from .backends.base import BackendReader
from .errors import ExtractionError, SizeLimitExceededError


_BACKEND_READ_SIZE = 64 * 1024


class ContentStream(io.RawIOBase):
    """Expose one backend payload through a conventional binary-I/O surface."""

    def __init__(
        self,
        backend: BackendReader,
        *,
        max_uncompressed_size: int | None = None,
    ) -> None:
        super().__init__()
        self._backend = backend
        self._backend_closed = False
        self._buffer = bytearray()
        self._accepted_bytes = 0
        self._eof = False
        self._max_size = _validate_max_size(max_uncompressed_size)

        declared_size = backend.declared_size
        if declared_size is not None and self._max_size is not None:
            if declared_size > self._max_size:
                self._abort()
                raise SizeLimitExceededError(
                    f"declared payload size {declared_size} exceeds limit "
                    f"{self._max_size}"
                )

    def readable(self) -> bool:
        self._checkClosed()
        return True

    def writable(self) -> bool:
        self._checkClosed()
        return False

    def read(self, size: int = -1) -> bytes:
        self._checkClosed()
        size = operator.index(size)
        if size == 0:
            return b""
        if size < 0:
            return self._read_all()

        if not self._buffer and not self._eof:
            self._pull()
        take = min(size, len(self._buffer))
        result = bytes(self._buffer[:take])
        del self._buffer[:take]
        return result

    def readinto(self, buffer) -> int:
        self._checkClosed()
        view = memoryview(buffer)
        if view.readonly:
            raise TypeError("readinto() argument must be writable")
        byte_view = view.cast("B")
        data = self.read(len(byte_view))
        byte_view[: len(data)] = data
        return len(data)

    def write(self, buffer) -> int:
        self._checkClosed()
        raise io.UnsupportedOperation("stream is not writable")

    def writelines(self, lines) -> None:
        self._checkClosed()
        raise io.UnsupportedOperation("stream is not writable")

    def truncate(self, size: int | None = None) -> int:
        self._checkClosed()
        raise io.UnsupportedOperation("stream is not writable")

    def close(self) -> None:
        if self.closed:
            return
        try:
            self._close_backend()
        finally:
            super().close()

    def _read_all(self) -> bytes:
        chunks: list[bytes] = []
        if self._buffer:
            chunks.append(bytes(self._buffer))
            self._buffer.clear()
        while not self._eof:
            self._pull()
            if self._buffer:
                chunks.append(bytes(self._buffer))
                self._buffer.clear()
        return b"".join(chunks)

    def _pull(self) -> None:
        request_size = _BACKEND_READ_SIZE
        if self._max_size is not None:
            remaining = self._max_size - self._accepted_bytes
            request_size = min(request_size, remaining + 1)

        try:
            data = self._backend.read(request_size)
        except BaseException:
            self._abort()
            raise

        if not isinstance(data, bytes):
            self._abort()
            raise ExtractionError("backend read() returned non-bytes data")
        if len(data) > request_size:
            self._abort()
            raise ExtractionError("backend read() exceeded its requested size")
        if not data:
            if not self._backend.completed:
                self._abort()
                raise ExtractionError("backend reported EOF before completion")
            self._eof = True
            self._close_backend()
            return

        new_total = self._accepted_bytes + len(data)
        if self._max_size is not None and new_total > self._max_size:
            self._abort()
            raise SizeLimitExceededError(
                f"actual payload size exceeds limit {self._max_size}"
            )
        self._accepted_bytes = new_total
        self._buffer.extend(data)

    def _close_backend(self, *, suppress: bool = False) -> None:
        if self._backend_closed:
            return
        self._backend_closed = True
        if suppress:
            try:
                self._backend.close()
            except BaseException:
                pass
        else:
            self._backend.close()

    def _abort(self) -> None:
        self._buffer.clear()
        self._close_backend(suppress=True)
        if not self.closed:
            super().close()


def _validate_max_size(value: int | None) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("max_uncompressed_size must be an integer or None")
    if value < 0:
        raise ValueError("max_uncompressed_size must be non-negative")
    return value
