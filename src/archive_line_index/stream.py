"""Owned sequential stream with retained failure and explicit closure states."""

from __future__ import annotations

import io
from types import TracebackType

from .backends.base import BackendReader
from .errors import ExtractionError, SizeLimitExceededError


class ContentStream:
    """Readable, nonseekable payload access; construct through open_content_stream.

    Instances own their reader. Callers serialize operations and close explicitly
    or use a context manager. This is a supported subset, not a full BinaryIO.
    A delivery failure releases resources and remains observable until explicit
    close; it never becomes successful EOF. Failed cleanup permits a close retry.
    Capability queries remain available in EOF/FAILED states while nonclosed.
    """

    _reader: BackendReader | None
    _failure: BaseException | None
    _closed: bool
    _eof: bool
    _limit: int | None
    _accepted: int

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
        if self._limit is not None:
            size = min(size, self._limit - self._accepted + 1)
        data = self._reader.read(size)
        if not isinstance(data, bytes) or len(data) > size:
            raise ExtractionError("backend returned invalid bounded bytes")
        self._accepted += len(data)
        if self._limit is not None and self._accepted > self._limit:
            raise SizeLimitExceededError(f"Payload exceeds {self._limit} bytes")
        if not data:
            if not self._reader.completed:
                raise ExtractionError(
                    "backend returned EOF without terminal validation"
                )
            self._eof = True
        return data

    def read(self, size: int = -1, /) -> bytes:
        """Read bytes, consuming through validated EOF for any negative size.

        Args:
            size: Maximum bytes, zero for no progress, or negative for all remaining.

        Raises:
            TypeError: If size is not an integer or is a bool.
            ValueError: If the stream is closed.
            SizeLimitExceededError: If actual payload bytes exceed the limit.

        A failing call returns no partial result, including unbounded reads.
        """
        self._check_open()
        if isinstance(size, bool) or not isinstance(size, int):
            raise TypeError("read size must be an integer")
        self._check_failure()
        if size == 0:
            return b""
        try:
            if size < 0:
                blocks: list[bytes] = []
                while block := self._read_block(1024 * 1024):
                    blocks.append(block)
                return b"".join(blocks)
            return self._read_block(size)
        except BaseException as error:
            self._fail(error)
            raise

    def readinto(self, buffer: object, /) -> int:
        """Read into writable contiguous storage, preserving its unused suffix.

        Capacity is measured in bytes, including for nonbyte array elements.
        Invalid buffers raise TypeError before any reader progress. Closed-state
        ValueError takes priority; otherwise buffer validation precedes a retained
        delivery failure. A zero-byte buffer makes no progress and proves no EOF.
        """
        self._check_open()
        try:
            original = memoryview(buffer)  # type: ignore[arg-type]
            try:
                if original.readonly or not original.c_contiguous:
                    raise TypeError("buffer must be writable and contiguous")
                view = original.cast("B")
            finally:
                original.release()
        except (TypeError, ValueError) as error:
            raise TypeError("buffer must support writable contiguous bytes") from error
        with view:
            self._check_failure()
            if not view.nbytes:
                return 0
            try:
                data = self._read_block(view.nbytes)
                view[: len(data)] = data
                return len(data)
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


def validate_stream_limit(max_uncompressed_size: int | None) -> None:
    """Validate an inclusive payload limit before source acquisition."""
    if max_uncompressed_size is None:
        return
    if isinstance(max_uncompressed_size, bool) or not isinstance(
        max_uncompressed_size, int
    ):
        raise TypeError("max_uncompressed_size must be None or an integer")
    if max_uncompressed_size < 0:
        raise ValueError("max_uncompressed_size must be nonnegative")


def make_content_stream(
    reader: BackendReader, *, max_uncompressed_size: int | None
) -> ContentStream:
    """Consume reader ownership at entry, closing it if construction fails."""
    try:
        validate_stream_limit(max_uncompressed_size)
        declared = reader.declared_size
        if (
            max_uncompressed_size is not None
            and declared is not None
            and declared > max_uncompressed_size
        ):
            raise SizeLimitExceededError(
                f"Declared payload size {declared} exceeds {max_uncompressed_size}"
            )
        stream = object.__new__(ContentStream)
        stream._reader = reader
        stream._failure = None
        stream._closed = False
        stream._eof = False
        stream._limit = max_uncompressed_size
        stream._accepted = 0
        return stream
    except BaseException as error:
        try:
            reader.close()
        except BaseException as cleanup:
            error.add_note(f"Payload cleanup failed: {cleanup!r}")
        raise
