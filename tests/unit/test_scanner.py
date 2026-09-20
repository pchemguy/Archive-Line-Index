"""Tests for bounded LF byte-line scanning."""

from __future__ import annotations

import inspect
import io

import pytest

import archive_line_index.scanner as scanner_module
from archive_line_index.scanner import scan_offsets
from tests.helpers.binary_cases import BINARY_CASES, UTF8_BOM
from tests.helpers.streams import FailingReadStream, ShortReadStream


@pytest.mark.parametrize("case", BINARY_CASES, ids=lambda case: case.name)
def test_canonical_binary_cases(case) -> None:
    offsets = scan_offsets(
        io.BytesIO(case.content),
        skip_utf8_bom=case.skip_bom,
        buffer_size=4,
    )
    assert tuple(offsets) == case.offsets


@pytest.mark.parametrize("case", BINARY_CASES, ids=lambda case: case.name)
@pytest.mark.parametrize("buffer_size", range(1, 8))
def test_results_are_invariant_across_scan_block_boundaries(
    case, buffer_size: int
) -> None:
    offsets = scan_offsets(
        io.BytesIO(case.content),
        skip_utf8_bom=case.skip_bom,
        buffer_size=buffer_size,
    )
    assert tuple(offsets) == case.offsets


@pytest.mark.parametrize("max_chunk", [1, 2])
def test_split_bom_and_arbitrary_short_reads(max_chunk: int) -> None:
    stream = ShortReadStream(UTF8_BOM + b"a\n\nb", max_chunk=max_chunk)
    offsets = scan_offsets(stream, skip_utf8_bom=True, buffer_size=8)
    assert tuple(offsets) == (3, 5, 6, 7)


def test_line_larger_than_buffer_is_not_accumulated() -> None:
    content = (b"x" * 200_000) + b"\nend"
    offsets = scan_offsets(io.BytesIO(content), skip_utf8_bom=True, buffer_size=31)
    assert tuple(offsets) == (0, 200_001, 200_004)


def test_scan_origin_is_the_streams_current_position() -> None:
    stream = io.BytesIO(b"ignored" + b"a\nb")
    stream.seek(len(b"ignored"))
    offsets = scan_offsets(stream, skip_utf8_bom=True, buffer_size=2)
    assert tuple(offsets) == (0, 2, 3)


def test_read_failure_propagates_without_a_partial_index() -> None:
    stream = FailingReadStream(b"a\nb\nc", fail_after_reads=2)
    with pytest.raises(OSError, match="controlled"):
        scan_offsets(stream, skip_utf8_bom=True, buffer_size=2)


def test_scanner_does_not_close_caller_stream() -> None:
    stream = io.BytesIO(b"a\n")
    assert tuple(scan_offsets(stream, skip_utf8_bom=True, buffer_size=1)) == (0, 2)
    assert not stream.closed


def test_text_reads_are_rejected() -> None:
    with pytest.raises(TypeError, match="must return bytes"):
        scan_offsets(io.StringIO("a\n"), skip_utf8_bom=True, buffer_size=4)


@pytest.mark.parametrize("buffer_size", [0, -1])
def test_nonpositive_buffer_size_is_rejected_before_read(buffer_size: int) -> None:
    stream = ShortReadStream(b"data", max_chunk=1)
    with pytest.raises(ValueError, match="positive"):
        scan_offsets(stream, skip_utf8_bom=True, buffer_size=buffer_size)
    assert stream.requests == []


@pytest.mark.parametrize("buffer_size", [True, 1.5, "4"])
def test_noninteger_buffer_size_is_rejected_before_read(buffer_size) -> None:
    stream = ShortReadStream(b"data", max_chunk=1)
    with pytest.raises(TypeError, match="integer"):
        scan_offsets(stream, skip_utf8_bom=True, buffer_size=buffer_size)
    assert stream.requests == []


def test_skip_bom_requires_an_actual_bool() -> None:
    stream = ShortReadStream(b"data", max_chunk=1)
    with pytest.raises(TypeError, match="bool"):
        scan_offsets(stream, skip_utf8_bom=1, buffer_size=4)
    assert stream.requests == []


def test_scanner_uses_native_find_not_python_byte_iteration() -> None:
    source = inspect.getsource(scanner_module)
    assert '.find(b"\\n"' in source
    assert "for byte in" not in source
    assert "for value in block" not in source
