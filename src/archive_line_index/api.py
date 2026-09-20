"""Public composition of source handling, content streaming, and indexing."""

from __future__ import annotations

import os
from array import array
from typing import BinaryIO

from .backends.registry import open_backend
from .formats import detect_format
from .scanner import scan_offsets
from .sources import Source, open_source
from .stream import ContentStream


DEFAULT_BUFFER_SIZE = 1024 * 1024


def open_content_stream(
    source: Source,
    *,
    max_uncompressed_size: int | None = None,
) -> ContentStream:
    """Open a plain payload or supported archive member as sequential bytes."""

    _validate_max_uncompressed_size(max_uncompressed_size)
    filename = source if isinstance(source, (str, os.PathLike)) else None
    handle = open_source(source)
    try:
        source_format = detect_format(handle, filename=filename)
        backend = open_backend(source_format, handle)
        return ContentStream(
            backend,
            max_uncompressed_size=max_uncompressed_size,
        )
    except BaseException:
        handle.close()
        raise


def scan_line_offsets(
    stream: BinaryIO,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> array:
    """Return line starts followed by an EOF sentinel."""

    return scan_offsets(
        stream,
        skip_utf8_bom=skip_utf8_bom,
        buffer_size=buffer_size,
    )


def build_line_index(
    source: Source,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
    max_uncompressed_size: int | None = None,
) -> array:
    """Open a source, scan its payload, and return its completed index."""

    _validate_scan_options(skip_utf8_bom, buffer_size)
    _validate_max_uncompressed_size(max_uncompressed_size)
    with open_content_stream(
        source,
        max_uncompressed_size=max_uncompressed_size,
    ) as stream:
        return scan_line_offsets(
            stream,
            skip_utf8_bom=skip_utf8_bom,
            buffer_size=buffer_size,
        )


def _validate_scan_options(skip_utf8_bom: bool, buffer_size: int) -> None:
    if not isinstance(skip_utf8_bom, bool):
        raise TypeError("skip_utf8_bom must be a bool")
    if not isinstance(buffer_size, int) or isinstance(buffer_size, bool):
        raise TypeError("buffer_size must be an integer")
    if buffer_size <= 0:
        raise ValueError("buffer_size must be positive")


def _validate_max_uncompressed_size(value: int | None) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("max_uncompressed_size must be an integer or None")
    if value < 0:
        raise ValueError("max_uncompressed_size must be non-negative")
