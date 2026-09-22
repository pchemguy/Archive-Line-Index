"""Public interface for archive line indexing."""

from .api import (
    DEFAULT_BUFFER_SIZE,
    build_line_index,
    open_content_stream,
    read_raw_index,
    read_sqlite_index,
    scan_line_offsets,
    write_raw_index,
    write_sqlite_index,
)
from .errors import (
    ArchiveLineIndexError,
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    InvalidIndexError,
    PersistenceError,
    SizeLimitExceededError,
    UnsupportedFormatError,
)
from .sources import Source
from .stream import ContentStream


__all__ = [
    "ArchiveLineIndexError",
    "ArchiveStructureError",
    "ContentStream",
    "DEFAULT_BUFFER_SIZE",
    "ExtractionError",
    "InvalidArchiveError",
    "InvalidIndexError",
    "PersistenceError",
    "SizeLimitExceededError",
    "Source",
    "UnsupportedFormatError",
    "build_line_index",
    "open_content_stream",
    "read_raw_index",
    "read_sqlite_index",
    "scan_line_offsets",
    "write_raw_index",
    "write_sqlite_index",
]
