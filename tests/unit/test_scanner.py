"""Generic LF scanning, read bounds and borrowed-stream ownership."""

import io
from collections.abc import Mapping

import pytest

from archive_line_index.offsets import validate_offsets
from archive_line_index.scanner import DEFAULT_BUFFER_SIZE, scan_line_offsets


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
