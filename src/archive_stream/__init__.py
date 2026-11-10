"""Sequential payload streaming and byte-line indexing."""

from .api import build_line_index, open_content_stream
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
from .persistence.raw import read_raw_index, write_raw_index
from .persistence.sqlite import read_sqlite_index, write_sqlite_index
from .scanner import DEFAULT_BUFFER_SIZE, ReadableBinary, scan_line_offsets
from .sources import Source
from .stream import ContentStream

__all__ = [
    "read_raw_index",
    "write_raw_index",
    "read_sqlite_index",
    "write_sqlite_index",
    "Source",
    "ReadableBinary",
    "DEFAULT_BUFFER_SIZE",
    "ContentStream",
    "open_content_stream",
    "scan_line_offsets",
    "build_line_index",
    "ArchiveLineIndexError",
    "ArchiveStructureError",
    "ExtractionError",
    "InvalidArchiveError",
    "InvalidIndexError",
    "PersistenceError",
    "SizeLimitExceededError",
    "UnsupportedFormatError",
]
