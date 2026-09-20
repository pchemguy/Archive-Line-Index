"""Bounded LF byte-line scanning over readable binary streams."""

from __future__ import annotations

from array import array
from typing import BinaryIO

from .errors import InvalidIndexError
from .offsets import MAX_OFFSET, validate_offset_array


UTF8_BOM = b"\xef\xbb\xbf"


def scan_offsets(
    stream: BinaryIO,
    *,
    skip_utf8_bom: bool,
    buffer_size: int,
) -> array:
    """Scan ``stream`` from its current position and return line starts plus EOF."""

    if not isinstance(skip_utf8_bom, bool):
        raise TypeError("skip_utf8_bom must be a bool")
    if not isinstance(buffer_size, int) or isinstance(buffer_size, bool):
        raise TypeError("buffer_size must be an integer")
    if buffer_size <= 0:
        raise ValueError("buffer_size must be positive")

    prefix = bytearray()
    while len(prefix) < len(UTF8_BOM):
        chunk = _read_bytes(stream, len(UTF8_BOM) - len(prefix))
        if not chunk:
            break
        prefix.extend(chunk)

    prefix_bytes = bytes(prefix)
    skipped_bom = skip_utf8_bom and prefix_bytes.startswith(UTF8_BOM)
    line_start = len(UTF8_BOM) if skipped_bom else 0
    stream_end = len(prefix_bytes)
    offsets = array("Q")

    def append_offset(value: int) -> None:
        if value > MAX_OFFSET:
            raise InvalidIndexError("indexed offset exceeds the supported range")
        offsets.append(value)

    def scan_block(block: bytes, block_start: int) -> None:
        nonlocal line_start
        search_from = 0
        while True:
            newline = block.find(b"\n", search_from)
            if newline < 0:
                return
            line_end = block_start + newline + 1
            append_offset(line_start)
            line_start = line_end
            search_from = newline + 1

    initial_start = len(UTF8_BOM) if skipped_bom else 0
    initial = prefix_bytes[initial_start:]
    if initial:
        scan_block(initial, initial_start)

    while True:
        block = _read_bytes(stream, buffer_size)
        if not block:
            break
        block_start = stream_end
        stream_end += len(block)
        if stream_end > MAX_OFFSET:
            raise InvalidIndexError("indexed size exceeds the supported range")
        scan_block(block, block_start)

    if line_start < stream_end:
        append_offset(line_start)
    append_offset(stream_end)
    return validate_offset_array(offsets)


def _read_bytes(stream: BinaryIO, size: int) -> bytes:
    data = stream.read(size)
    if not isinstance(data, bytes):
        raise TypeError("stream read() must return bytes")
    return data
