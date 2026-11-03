"""Owned sequential stream with retained failure and explicit closure states."""

from __future__ import annotations

import io
from types import TracebackType

from .backends.base import BackendReader
from .errors import ExtractionError


class ContentStream:
    """Readable, nonseekable payload access; construct through open_content_stream.

    Instances own their reader. Callers serialize operations and close explicitly
    or use a context manager. This is a supported subset, not a full BinaryIO.
    """

    _reader: BackendReader | None
    _failure: BaseException | None
    _closed: bool
    _eof: bool

    def __init__(self) -> None:
        raise TypeError("use open_content_stream to construct a ContentStream")

    @property
    def closed(self) -> bool:
        """Whether explicit resource closure completed successfully."""
        return self._closed

    def _check_open(self) -> None:
        if self._closed:
            raise ValueError("operation on closed content stream")

    def _check_failure(self) -> None:
        if self._failure is not None:
            raise self._failure

    def _release(self) -> None:
        if self._reader is not None:
            self._reader.close()
            self._reader = None

    def _fail(self, error: BaseException) -> None:
        self._failure = error
        try:
            self._release()
        except BaseException as cleanup:
            error.add_note(f"Payload cleanup failed: {cleanup!r}")

    def _read_block(self, size: int) -> bytes:
        if self._eof:
            return b""
        assert self._reader is not None
        data = self._reader.read(size)
        if not isinstance(data, bytes) or len(data) > size:
            raise ExtractionError("backend returned invalid bounded bytes")
        if not data:
            if not self._reader.completed:
                raise ExtractionError(
                    "backend returned EOF without terminal validation"
                )
            self._eof = True
        return data

    def read(self, size: int = -1, /) -> bytes:
        """Return at most size bytes; zero reads do not advance the reader."""
        self._check_open()
        if isinstance(size, bool) or not isinstance(size, int):
            raise TypeError("read size must be an integer")
        self._check_failure()
        if size == 0:
            return b""
        if size < 0:
            raise io.UnsupportedOperation("unbounded reads are not delivered yet")
        try:
            return self._read_block(size)
        except BaseException as error:
            self._fail(error)
            raise

    def readable(self) -> bool:
        """Return True while nonclosed, including after EOF or failure."""
        self._check_open()
        return True

    def writable(self) -> bool:
        """Return False while nonclosed."""
        self._check_open()
        return False

    def seekable(self) -> bool:
        """Return False while nonclosed."""
        self._check_open()
        return False

    def seek(self, offset: int, whence: int = 0, /) -> int:
        """Reject positioning; payload access is sequential."""
        self._check_open()
        raise io.UnsupportedOperation("content stream is not seekable")

    def tell(self) -> int:
        """Reject positioning; no public cursor API is supported."""
        self._check_open()
        raise io.UnsupportedOperation("content stream has no position API")

    def write(self, data: object, /) -> int:
        """Reject writes to payload content."""
        self._check_open()
        raise io.UnsupportedOperation("content stream is not writable")

    def close(self) -> None:
        """Release resources, allowing retry if cleanup raises."""
        if self._closed:
            return
        self._release()
        self._closed = True

    def __enter__(self) -> ContentStream:
        self._check_open()
        self._check_failure()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            self.close()
        except BaseException as cleanup:
            if exc_value is None:
                raise
            exc_value.add_note(f"Payload cleanup failed: {cleanup!r}")


def make_content_stream(
    reader: BackendReader, *, max_uncompressed_size: int | None
) -> ContentStream:
    """Consume an owned reader and create its common stream."""
    stream = object.__new__(ContentStream)
    stream._reader = reader
    stream._failure = None
    stream._closed = False
    stream._eof = False
    return stream
