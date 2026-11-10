"""Generic LF scanning, read bounds and borrowed-stream ownership."""

import io
from collections.abc import Mapping

import pytest

from archive_stream.offsets import validate_offsets
from archive_stream.scanner import DEFAULT_BUFFER_SIZE, scan_line_offsets


@pytest.mark.parametrize(
    "payload,expected",
    [
        (b"", [0]),
        (b"abc", [0, 3]),
        (b"abc\n", [0, 4]),
        (b"abc\r\n", [0, 5]),
        (b"abc\rdef", [0, 7]),
        (b"\n", [0, 1]),
        (b"\n\n", [0, 1, 2]),
        (b"a\n\nb", [0, 2, 3, 4]),
        (b"a\x00\xff\nb", [0, 4, 5]),
    ],
)
@pytest.mark.parametrize("buffer_size", [1, 2, 3, 4, 7])
def test_exact_lf_examples(
    payload: bytes, expected: list[int], buffer_size: int
) -> None:
    source = io.BytesIO(payload)
    offsets = scan_line_offsets(source, buffer_size=buffer_size)
    assert offsets.tolist() == expected
    assert offsets.typecode == "Q" and offsets.itemsize == 8
    validate_offsets(offsets)
    assert not source.closed and source.tell() == len(payload)


def test_current_position_is_local_zero_and_short_reads_are_legal() -> None:
    class Short(io.BytesIO):
        def read(self, size: int = -1, /) -> bytes:
            assert 0 < size <= 4
            return super().read(min(size, 2))

    source = Short(b"skip:a\nb\nend")
    source.seek(5)
    assert scan_line_offsets(source, buffer_size=4).tolist() == [0, 2, 4, 7]
    assert not source.closed
    assert DEFAULT_BUFFER_SIZE == 1024 * 1024


@pytest.mark.parametrize(
    "options,exc",
    [
        ({"buffer_size": 0}, ValueError),
        ({"buffer_size": -1}, ValueError),
        ({"buffer_size": True}, TypeError),
        ({"buffer_size": 1.0}, TypeError),
        ({"skip_utf8_bom": 1}, TypeError),
        ({"skip_utf8_bom": None}, TypeError),
    ],
)
def test_invalid_options_before_io(
    options: Mapping[str, object], exc: type[Exception]
) -> None:
    class Unreadable:
        def read(self, size: int = -1, /) -> bytes:
            pytest.fail("invalid options performed IO")

    with pytest.raises(exc):
        scan_line_offsets(Unreadable(), **options)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "result", [None, "text", bytearray(b"x"), memoryview(b"x"), b"oversized"]
)
def test_invalid_reader_results(result: object) -> None:
    class Bad:
        def read(self, size: int = -1, /) -> bytes:
            return result  # type: ignore[return-value]

    with pytest.raises(TypeError):
        scan_line_offsets(Bad(), buffer_size=1)


@pytest.mark.parametrize("source", [object(), None, type("Bad", (), {"read": 1})()])
def test_missing_read_operation(source: object) -> None:
    with pytest.raises(TypeError):
        scan_line_offsets(source)  # type: ignore[arg-type]


def test_read_failure_propagates_without_closing_borrowed_source() -> None:
    error = OSError("caller read")

    class Fails(io.BytesIO):
        def read(self, size: int = -1, /) -> bytes:
            raise error

    source = Fails()
    with pytest.raises(OSError) as caught:
        scan_line_offsets(source)
    assert caught.value is error and not source.closed


@pytest.mark.parametrize(
    "payload,skipped",
    [
        (b"\xef\xbb\xbf", [3]),
        (b"\xef\xbb\xbfabc\n", [3, 7]),
        (b"\xef\xbb\xbf\n", [3, 4]),
        (b"\xef\xbb\xbf\xef\xbb\xbf", [3, 6]),
        (b"\xef", [0, 1]),
        (b"\xef\xbb", [0, 2]),
        (b"\xef\xbbX\n", [0, 4]),
        (b"x\xef\xbb\xbf", [0, 4]),
    ],
)
@pytest.mark.parametrize("buffer_size", [1, 2, 3, 4, 9])
def test_bom_policy_at_every_probe_boundary(
    payload: bytes, skipped: list[int], buffer_size: int
) -> None:
    assert (
        scan_line_offsets(io.BytesIO(payload), buffer_size=buffer_size).tolist()
        == skipped
    )
    expected = [0] + [i + 1 for i, b in enumerate(payload) if b == 10]
    if expected[-1] != len(payload):
        expected.append(len(payload))
    assert (
        scan_line_offsets(
            io.BytesIO(payload), skip_utf8_bom=False, buffer_size=buffer_size
        ).tolist()
        == expected
    )


def test_random_legal_short_reads_preserve_exact_coordinates() -> None:
    import random

    rng = random.Random(4732)
    for _ in range(100):
        payload = b"\xef\xbb\xbf" + bytes(
            rng.choice([0, 10, 13, 65, 239, 255]) for _ in range(rng.randrange(200))
        )

        class Short(io.BytesIO):
            def read(self, size: int = -1, /) -> bytes:
                assert 0 < size <= 11
                return super().read(rng.randint(1, size))

        expected = [3] + [i + 1 for i in range(3, len(payload)) if payload[i] == 10]
        if expected[-1] != len(payload):
            expected.append(len(payload))
        assert scan_line_offsets(Short(payload), buffer_size=11).tolist() == expected


def test_overflow_rejected_without_closing_borrowed_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from archive_stream import offsets
    from archive_stream.errors import InvalidIndexError

    monkeypatch.setattr(offsets, "MAX_OFFSET", 5)
    source = io.BytesIO(b"abcdef")
    with pytest.raises(InvalidIndexError):
        scan_line_offsets(source, buffer_size=2)
    assert not source.closed


def test_allocation_and_native_width_fail_before_reading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from array import array

    from archive_stream import scanner
    from archive_stream.errors import InvalidIndexError

    source = io.BytesIO(b"data")

    def fail(*args: object) -> object:
        raise MemoryError("index allocation")

    monkeypatch.setattr(scanner, "array", fail)
    with pytest.raises(MemoryError, match="index allocation"):
        scan_line_offsets(source)
    assert source.tell() == 0 and not source.closed
    monkeypatch.setattr(scanner, "array", lambda *args: array("I", [0]))
    with pytest.raises(InvalidIndexError):
        scan_line_offsets(source)
    assert source.tell() == 0 and not source.closed


def test_append_allocation_failure_returns_no_partial_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from archive_stream import scanner

    source = io.BytesIO(b"line\nnext")

    def fail(*args: object) -> None:
        raise MemoryError("append allocation")

    monkeypatch.setattr(scanner, "append_offset", fail)
    with pytest.raises(MemoryError, match="append allocation"):
        scan_line_offsets(source, buffer_size=2)
    assert not source.closed


def test_late_borrowed_read_error_does_not_return_a_partial_index() -> None:
    from tests.helpers.readers import Reader

    error = OSError("late caller failure")
    source = Reader(b"a\n", b"b", error)
    with pytest.raises(OSError) as caught:
        scan_line_offsets(source, buffer_size=2)  # type: ignore[arg-type]
    assert caught.value is error and source.closes == 0
    assert all(0 < n <= 2 for n in source.requests)
