"""Bounded native LF search over borrowed blocking binary readers."""

from __future__ import annotations

from array import array
from typing import Protocol

from .errors import InvalidIndexError
from .offsets import append_offset, check_position, validate_offsets

DEFAULT_BUFFER_SIZE = 1024 * 1024


class ReadableBinary(Protocol):
    """Minimal blocking read interface; no positioning or close is required."""

    def read(self, size: int = -1, /) -> bytes:
        """Return at most size bytes; empty bytes mean EOF."""
        ...


def validate_scan_options(*, skip_utf8_bom: bool, buffer_size: int) -> None:
    """Validate scan options before reading any input."""
    if not isinstance(skip_utf8_bom, bool):
        raise TypeError("skip_utf8_bom must be a bool")
    if isinstance(buffer_size, bool) or not isinstance(buffer_size, int):
        raise TypeError("buffer_size must be an integer")
    if buffer_size <= 0:
        raise ValueError("buffer_size must be positive")


def _read_block(stream: ReadableBinary, size: int) -> bytes:
    block = stream.read(size)
    if not isinstance(block, bytes) or len(block) > size:
        raise TypeError("read must return bytes no longer than requested")
    return block


def _scan_block(offsets: array[int], block: bytes, position: int) -> int:
    end = position + len(block)
    check_position(end)
    start = 0
    while (newline := block.find(b"\n", start)) >= 0:
        append_offset(offsets, position + newline + 1)
        start = newline + 1
    return end


def scan_line_offsets(
    stream: ReadableBinary,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> array[int]:
    """Return canonical LF offsets from the reader's current position.

    Args:
        stream: Borrowed blocking binary source, never closed or repositioned.
        skip_utf8_bom: Exclude exactly one initial UTF-8 BOM from line content.
        buffer_size: Positive maximum size of each requested block.

    Returns:
        Eight-byte unsigned offsets, with one EOF sentinel after the line starts.

    Raises:
        TypeError: If options or reader results violate their types/bounds.
        ValueError: If buffer_size is nonpositive.
        InvalidIndexError: If a coordinate or native array is unrepresentable.
        MemoryError: If index allocation fails; no partial result is returned.

    Caller read exceptions propagate unchanged. Working payload storage contains
    only a current block and up to three initial probe bytes, never a full line.
    A trailing LF creates no extra empty line; coordinates include skipped BOM
    bytes. The last value is EOF, and len(result) - 1 is the line count.
    """
    validate_scan_options(skip_utf8_bom=skip_utf8_bom, buffer_size=buffer_size)
    if not callable(getattr(stream, "read", None)):
        raise TypeError("stream must provide callable read")
    offsets = array("Q", [0])
    if offsets.itemsize != 8:
        raise InvalidIndexError("Native unsigned Q offsets require eight-byte items")
    prefix = b""
    exhausted = False
    while len(prefix) < 3:
        block = _read_block(stream, min(buffer_size, 3 - len(prefix)))
        if not block:
            exhausted = True
            break
        prefix += block
    if skip_utf8_bom and prefix == b"\xef\xbb\xbf":
        offsets[0] = 3
        position = 3
        check_position(position)
    else:
        position = _scan_block(offsets, prefix, 0)
    if not exhausted:
        while block := _read_block(stream, buffer_size):
            position = _scan_block(offsets, block, position)
    if offsets[-1] != position:
        append_offset(offsets, position)
    validate_offsets(offsets)
    return offsets
