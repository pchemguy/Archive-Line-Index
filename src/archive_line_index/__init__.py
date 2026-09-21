"""Public interface for archive line indexing."""

from .api import (
    DEFAULT_BUFFER_SIZE,
    build_line_index,
    open_content_stream,
    scan_line_offsets,
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
    "scan_line_offsets",
]
