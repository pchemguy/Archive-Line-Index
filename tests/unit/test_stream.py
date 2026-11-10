"""Stream state, validation priority and owned cleanup contracts."""

import gc
import io
import weakref
from collections.abc import Callable

import pytest
from tests.helpers.readers import Reader

from archive_stream.errors import ExtractionError
from archive_stream.stream import ContentStream, make_content_stream


def test_zero_short_and_terminal_reads() -> None:
    r = Reader(b"a", b"bc")
    s = make_content_stream(r, max_uncompressed_size=None)
    assert s.read(0) == b""
    assert not r.requests
    assert s.read(9) == b"a"
    assert s.read(9) == b"bc"
    assert s.read(9) == b""
    requests = list(r.requests)
    assert s.read(2) == b""
    assert r.requests == requests
    assert (s.readable(), s.writable(), s.seekable()) == (True, False, False)
    s.close()
    s.close()
    assert r.closes == 1 and s.closed


@pytest.mark.parametrize("size", [None, True, 1.5, "1"])
def test_invalid_size_without_progress(size: object) -> None:
    r = Reader(b"x")
    with make_content_stream(r, max_uncompressed_size=None) as s:
        with pytest.raises(TypeError):
            s.read(size)  # type: ignore[arg-type]
        assert not r.requests
        assert s.read(1) == b"x"


def test_retained_failure_and_nonclosed_validation_priority() -> None:
    error = OSError("delivery")
    r = Reader(b"x", error)
    s = make_content_stream(r, max_uncompressed_size=None)
    assert s.read(1) == b"x"
    for operation in (lambda: s.read(1), lambda: s.read(0), s.__enter__):
        with pytest.raises(OSError) as caught:
            operation()
        assert caught.value is error
    with pytest.raises(TypeError):
        s.read(True)
    assert not s.closed and r.closes == 1
    assert s.readable()
    s.close()
    assert s.closed and r.closes == 1


@pytest.mark.parametrize("bad", [None, "x", b"too long", b""])
def test_reader_protocol_violation_is_failure(bad: object) -> None:
    class BadReader(Reader):
        def read(self, size: int, /) -> bytes:
            return bad  # type: ignore[return-value]

    r = BadReader()
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(ExtractionError):
        s.read(1)
    assert not s.closed and r.closes == 1
    s.close()


def test_capability_rejections_and_closed_priority() -> None:
    s = make_content_stream(Reader(), max_uncompressed_size=None)
    unsupported: list[Callable[[], object]] = [
        lambda: s.seek(0),
        s.tell,
        lambda: s.write(b"x"),
    ]
    for op in unsupported:
        with pytest.raises(io.UnsupportedOperation):
            op()
    s.close()
    for op in unsupported + [
        lambda: s.read(None),
        s.readable,
        s.writable,
        s.seekable,
        s.__enter__,
    ]:  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            op()


def test_close_failure_can_retry_without_false_closed_claim() -> None:
    r = Reader(close_failures=1)
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(OSError, match="close fault"):
        s.close()
    assert not s.closed
    s.close()
    assert s.closed and r.closes == 2


def test_context_preserves_body_exception_with_cleanup_note() -> None:
    body = RuntimeError("consumer")
    r = Reader(close_failures=1)
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(RuntimeError) as caught, s:
        raise body
    assert caught.value is body
    assert "close fault" in body.__notes__[0]
    assert not s.closed
    s.close()


def test_delivery_failure_survives_cleanup_failure() -> None:
    error = MemoryError("allocation")
    r = Reader(error, close_failures=1)
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(MemoryError) as caught:
        s.read(1)
    assert caught.value is error and "close fault" in error.__notes__[0]
    s.close()
    assert s.closed and r.closes == 2


def test_backend_constructor_is_not_public() -> None:
    with pytest.raises(TypeError):
        ContentStream()


def test_unbounded_short_reads_and_late_failure() -> None:
    with make_content_stream(Reader(b"a", b"bc"), max_uncompressed_size=None) as s:
        assert s.read(-99) == b"abc"
        assert s.read() == b""
    error = ExtractionError("late integrity failure")
    r = Reader(b"valid prefix", error)
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(ExtractionError) as caught:
        s.read()
    assert caught.value is error and r.closes == 1
    s.close()


def test_readinto_byte_capacity_and_unchanged_tail() -> None:
    from array import array

    r = Reader(b"abcdef")
    with make_content_stream(r, max_uncompressed_size=None) as s:
        storage = array("I", [0xFFFFFFFF, 0xFFFFFFFF])
        raw = memoryview(storage).cast("B")
        assert s.readinto(storage) == 6
        assert bytes(raw) == b"abcdef\xff\xff"
        assert r.requests == [8]
        assert s.readinto(storage) == 0
        assert bytes(raw) == b"abcdef\xff\xff"


@pytest.mark.parametrize(
    "buffer", [b"readonly", object(), memoryview(bytearray(4))[::2]]
)
def test_readinto_rejection_has_no_progress(buffer: object) -> None:
    r = Reader(b"abc")
    with make_content_stream(r, max_uncompressed_size=None) as s:
        with pytest.raises(TypeError):
            s.readinto(buffer)
        assert not r.requests
        assert s.readinto(bytearray()) == 0
        assert not r.requests
        target = bytearray(b"?????")
        assert s.readinto(target) == 3
        assert target == b"abc??"


def test_readinto_closed_failure_and_argument_priority() -> None:
    r = Reader(OSError("failed"))
    s = make_content_stream(r, max_uncompressed_size=None)
    with pytest.raises(OSError):
        s.readinto(bytearray(1))
    with pytest.raises(TypeError):
        s.readinto(b"invalid")
    with pytest.raises(OSError):
        s.readinto(bytearray())
    s.close()
    with pytest.raises(ValueError):
        s.readinto(b"invalid")


@pytest.mark.parametrize("data,limit", [(b"", 0), (b"abc", 3), (b"abc", 100)])
def test_inclusive_actual_limits(data: bytes, limit: int) -> None:
    r = Reader(data)
    with make_content_stream(r, max_uncompressed_size=limit) as s:
        assert s.read() == data
        assert r.completed


@pytest.mark.parametrize("operation", ["read", "readinto", "unbounded"])
def test_crossing_actual_limit_returns_no_triggering_data(operation: str) -> None:
    from archive_stream.errors import SizeLimitExceededError

    r = Reader(b"a", b"bc", declared_size=0)
    s = make_content_stream(r, max_uncompressed_size=2)
    assert s.read(1) == b"a"
    target = bytearray(b"????")
    with pytest.raises(SizeLimitExceededError):
        if operation == "readinto":
            s.readinto(target)
        else:
            s.read(-1 if operation == "unbounded" else 99)
    assert target == b"????"
    assert r.closes == 1 and not s.closed
    s.close()


def test_declared_oversize_rejects_before_delivery_and_cleans() -> None:
    from archive_stream.errors import SizeLimitExceededError

    r = Reader(b"abc", declared_size=3)
    with pytest.raises(SizeLimitExceededError):
        make_content_stream(r, max_uncompressed_size=2)
    assert not r.requests and r.closes == 1


@pytest.mark.parametrize(
    "limit,exc", [(True, TypeError), (1.1, TypeError), (-1, ValueError)]
)
def test_invalid_construction_limit_consumes_reader(
    limit: object, exc: type[Exception]
) -> None:
    r = Reader()
    with pytest.raises(exc):
        make_content_stream(r, max_uncompressed_size=limit)  # type: ignore[arg-type]
    assert r.closes == 1 and not r.requests


def test_exact_limit_still_requires_terminal_validation() -> None:
    r = Reader(b"x", ExtractionError("footer"), declared_size=1)
    with make_content_stream(r, max_uncompressed_size=1) as s:
        assert s.read(1) == b"x"
        assert s.read(0) == b""
        with pytest.raises(ExtractionError, match="footer"):
            s.read(1)


def test_context_cleanup_failure_without_body_is_raised() -> None:
    s = make_content_stream(Reader(close_failures=1), max_uncompressed_size=None)
    with pytest.raises(OSError, match="close fault"), s:
        pass
    assert not s.closed
    s.close()


def test_construction_error_preserves_cleanup_failure_note() -> None:
    from archive_stream.errors import SizeLimitExceededError

    r = Reader(declared_size=3, close_failures=1)
    with pytest.raises(SizeLimitExceededError) as caught:
        make_content_stream(r, max_uncompressed_size=0)
    assert "close fault" in caught.value.__notes__[0]
    r.close()


def test_released_buffer_is_type_error_without_backend_work() -> None:
    view = memoryview(bytearray(2))
    view.release()
    r = Reader(b"x")
    with make_content_stream(r, max_uncompressed_size=None) as s:
        with pytest.raises(TypeError):
            s.readinto(view)
        assert not r.requests


def test_incompatible_buffer_provider_has_type_error_without_progress() -> None:
    import sys

    if sys.version_info < (3, 12):
        pytest.skip("Python-level buffer protocol requires Python 3.12")

    class IncompatibleBuffer:
        def __buffer__(self, flags: int) -> memoryview:
            raise BufferError("buffer unavailable")

    r = Reader(b"x")
    with make_content_stream(r, max_uncompressed_size=None) as s:
        with pytest.raises(TypeError):
            s.readinto(IncompatibleBuffer())
        assert not r.requests
        assert s.read(1) == b"x"


def test_successful_close_releases_failed_unbounded_read_frames() -> None:
    class Marker:
        pass

    marker_ref: weakref.ReferenceType[Marker] | None = None

    class FailingReader(Reader):
        calls = 0

        def read(self, size: int, /) -> bytes:
            nonlocal marker_ref
            self.calls += 1
            if self.calls > 4:
                marker = Marker()
                marker_ref = weakref.ref(marker)
                raise OSError("late delivery failure")
            return b"x" * min(size, 1024 * 1024)

    reader = FailingReader()
    stream = make_content_stream(reader, max_uncompressed_size=None)
    try:
        stream.read()
    except OSError:
        pass
    else:
        pytest.fail("late failure was not raised")
    gc.collect()
    assert marker_ref is not None and marker_ref() is not None
    assert not stream.closed
    stream.close()
    gc.collect()
    assert stream.closed and reader.closes == 1
    assert marker_ref() is None


def test_close_retry_preserves_retained_error_and_external_evidence() -> None:
    error = OSError("delivery")
    error.add_note("external context")
    reader = Reader(error, close_failures=2)
    stream = make_content_stream(reader, max_uncompressed_size=None)
    with pytest.raises(OSError, match="delivery"):
        stream.read()
    with pytest.raises(OSError, match="close fault"):
        stream.close()
    assert not stream.closed
    with pytest.raises(OSError) as caught:
        stream.read(0)
    assert caught.value is error
    traceback = error.__traceback__
    notes = tuple(error.__notes__)
    stream.close()
    assert stream.closed and reader.closes == 3
    assert error.__traceback__ is traceback and tuple(error.__notes__) == notes
    with pytest.raises(ValueError, match="closed"):
        stream.read(0)
