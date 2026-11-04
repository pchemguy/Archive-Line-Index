"""Public source operations composed from their owning providers."""

from __future__ import annotations

from array import array

from .backends.registry import open_backend
from .formats import detect_format
from .scanner import DEFAULT_BUFFER_SIZE, scan_line_offsets, validate_scan_options
from .sources import Source, normalize_source
from .stream import ContentStream, make_content_stream, validate_stream_limit


def open_content_stream(
    source: Source, *, max_uncompressed_size: int | None = None
) -> ContentStream:
    """Open sequential binary payload access, transferring ownership to the caller.

    Args:
        source: Stable text filesystem path; no URLs or bytes paths.
        max_uncompressed_size: Inclusive payload-byte limit, or None for no limit.

    Returns:
        An owned readable stream. Close it explicitly or use a context manager.

    Raises:
        TypeError: If a source or option has the wrong kind.
        ValueError: If the limit is negative.
        UnsupportedFormatError: If encryption or a required archive dependency/codec is unsupported.
        SizeLimitExceededError: If trustworthy size metadata exceeds the limit.
        OSError: If filesystem acquisition fails.
    """
    validate_stream_limit(max_uncompressed_size)
    path = normalize_source(source)
    candidate = detect_format(path)
    reader = open_backend(path, candidate)
    return make_content_stream(reader, max_uncompressed_size=max_uncompressed_size)


def build_line_index(
    source: Source,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
    max_uncompressed_size: int | None = None,
) -> array[int]:
    """Build a canonical byte-line index from a source, closing all owned resources.

    Args:
        source: Stable text filesystem path.
        skip_utf8_bom: Exclude one initial UTF-8 BOM from first-line content.
        buffer_size: Positive maximum scanner read size; defaults to 1 MiB.
        max_uncompressed_size: Inclusive payload-byte limit before BOM handling.

    Returns:
        Q/eight-byte line starts followed by EOF, relative to original bytes.

    All non-I/O arguments are checked before source acquisition. Read/allocation
    failures return no partial index. Mandatory cleanup must also succeed.
    """
    validate_scan_options(skip_utf8_bom=skip_utf8_bom, buffer_size=buffer_size)
    validate_stream_limit(max_uncompressed_size)
    path = normalize_source(source)
    with open_content_stream(
        path, max_uncompressed_size=max_uncompressed_size
    ) as stream:
        return scan_line_offsets(
            stream, skip_utf8_bom=skip_utf8_bom, buffer_size=buffer_size
        )
