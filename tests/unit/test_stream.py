"""Tests for the backend reader contract and common content stream."""

import io

import pytest

from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.plain import open_plain_backend
from archive_line_index.errors import ExtractionError, SizeLimitExceededError
from archive_line_index.sources import open_source
from archive_line_index.stream import ContentStream


class FakeBackendReader:
    def __init__(self, data: bytes, *, declared_size: int | None = None) -> None:
        self._data = data
        self._position = 0
        self._declared_size = declared_size
        self._completed = False
        self.closed = False
        self.read_calls = 0

    @property
    def declared_size(self) -> int | None:
        return self._declared_size

    @property
    def completed(self) -> bool:
        return self._completed

    def read(self, size: int) -> bytes:
        self.read_calls += 1
        if self.closed:
            raise ValueError("reader is closed")
        chunk = self._data[self._position : self._position + size]
        self._position += len(chunk)
        if not chunk:
            self._completed = True
        return chunk

    def close(self) -> None:
        self.closed = True


def test_fake_reader_satisfies_backend_protocol() -> None:
    reader = FakeBackendReader(b"payload", declared_size=7)

    assert isinstance(reader, BackendReader)
    assert reader.declared_size == 7
    assert not reader.completed
    assert reader.read(4) == b"payl"
    assert reader.read(4) == b"oad"
    assert reader.read(4) == b""
    assert reader.completed


def test_backend_contract_requires_completion_and_metadata() -> None:
    class IncompleteReader:
        def read(self, size: int) -> bytes:
            return b""

        def close(self) -> None:
            pass

    assert not isinstance(IncompleteReader(), BackendReader)


def test_backend_close_is_available_to_common_stream() -> None:
    reader = FakeBackendReader(b"")
    reader.close()
    assert reader.closed


@pytest.mark.parametrize(
    ("size", "expected"),
    [(0, b""), (1, b"p"), (4, b"payl"), (100, b"payload"), (-1, b"payload")],
)
def test_read_sizes_follow_binary_io_behavior(size: int, expected: bytes) -> None:
    backend = FakeBackendReader(b"payload")
    stream = ContentStream(backend)

    assert stream.read(size) == expected
    if size == 0:
        assert backend.read_calls == 0


def test_repeated_bounded_reads_and_eof() -> None:
    backend = FakeBackendReader(b"payload")
    stream = ContentStream(backend)

    assert stream.read(3) == b"pay"
    assert stream.read(3) == b"loa"
    assert stream.read(3) == b"d"
    assert stream.read(3) == b""
    calls_at_eof = backend.read_calls
    assert stream.read(3) == b""
    assert backend.read_calls == calls_at_eof
    assert backend.closed


def test_readinto_writes_only_returned_bytes() -> None:
    stream = ContentStream(FakeBackendReader(b"abc"))
    destination = bytearray(b"xxxxx")

    assert stream.readinto(memoryview(destination)[1:4]) == 3
    assert destination == bytearray(b"xabcx")
    assert stream.readinto(bytearray()) == 0


def test_readinto_rejects_readonly_buffer() -> None:
    stream = ContentStream(FakeBackendReader(b"abc"))
    with pytest.raises(TypeError, match="writable"):
        stream.readinto(b"xxx")


@pytest.mark.parametrize("limit", [0, 3])
def test_exact_size_limit_is_inclusive(limit: int) -> None:
    content = b"abc"[:limit]
    stream = ContentStream(FakeBackendReader(content), max_uncompressed_size=limit)
    assert stream.read() == content


def test_declared_size_limit_rejects_before_read_and_closes() -> None:
    backend = FakeBackendReader(b"payload", declared_size=7)
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)
    assert backend.read_calls == 0
    assert backend.closed


def test_actual_size_limit_rejects_first_excess_without_delivery() -> None:
    backend = FakeBackendReader(b"abcd", declared_size=None)
    stream = ContentStream(backend, max_uncompressed_size=3)
    with pytest.raises(SizeLimitExceededError, match="actual"):
        stream.read(1)
    assert stream.closed
    assert backend.closed


@pytest.mark.parametrize("limit", [True, -1, 1.5, "3"])
def test_invalid_size_limit_is_rejected(limit) -> None:
    backend = FakeBackendReader(b"")
    with pytest.raises((TypeError, ValueError)):
        ContentStream(backend, max_uncompressed_size=limit)


def test_backend_failure_closes_stream_and_propagates() -> None:
    class FailingBackend(FakeBackendReader):
        def read(self, size: int) -> bytes:
            raise OSError("backend failed")

    backend = FailingBackend(b"")
    stream = ContentStream(backend)
    with pytest.raises(OSError, match="backend failed"):
        stream.read(1)
    assert stream.closed
    assert backend.closed


def test_false_eof_is_extraction_error() -> None:
    class FalseEofBackend(FakeBackendReader):
        def read(self, size: int) -> bytes:
            return b""

    backend = FalseEofBackend(b"")
    stream = ContentStream(backend)
    with pytest.raises(ExtractionError, match="before completion"):
        stream.read(1)
    assert stream.closed


def test_capabilities_and_unsupported_operations() -> None:
    stream = ContentStream(FakeBackendReader(b"payload"))
    assert stream.readable()
    assert not stream.writable()
    assert not stream.seekable()
    with pytest.raises(io.UnsupportedOperation):
        stream.seek(0)
    with pytest.raises(io.UnsupportedOperation):
        stream.write(b"x")
    with pytest.raises(io.UnsupportedOperation):
        stream.truncate()


def test_close_is_idempotent_and_closed_operations_fail() -> None:
    backend = FakeBackendReader(b"payload")
    stream = ContentStream(backend)
    stream.close()
    stream.close()
    assert backend.closed
    with pytest.raises(ValueError):
        stream.read(1)
    with pytest.raises(ValueError):
        stream.readable()


def test_context_exit_after_consumer_exception_closes_backend() -> None:
    backend = FakeBackendReader(b"payload")
    with pytest.raises(RuntimeError, match="consumer"):
        with ContentStream(backend) as stream:
            assert stream.read(1) == b"p"
            raise RuntimeError("consumer failed")
    assert backend.closed


def test_plain_backend_cleanup_preserves_caller_source() -> None:
    source = io.BytesIO(b"payload")
    stream = ContentStream(open_plain_backend(open_source(source)))
    assert stream.read() == b"payload"
    stream.close()
    assert not source.closed
