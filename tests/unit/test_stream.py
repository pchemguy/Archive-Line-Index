"""Stream state, validation priority and owned cleanup contracts."""

import io
from collections.abc import Callable

import pytest
from tests.helpers.readers import Reader

from archive_line_index.errors import ExtractionError
from archive_line_index.stream import ContentStream, make_content_stream


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
