"""Public composition of source handling, content streaming, and indexing."""

from __future__ import annotations

from array import array
from os import PathLike
from typing import BinaryIO

from .backends.registry import open_backend
from .formats import detect_format
from .persistence.raw import read_raw_index as _read_raw_index
from .persistence.raw import write_raw_index as _write_raw_index
from .persistence.sqlite import read_sqlite_index as _read_sqlite_index
from .persistence.sqlite import write_sqlite_index as _write_sqlite_index
from .scanner import scan_offsets
from .sources import Source, normalize_source_path
from .stream import ContentStream


DEFAULT_BUFFER_SIZE = 1024 * 1024


def open_content_stream(
    source: Source,
    *,
    max_uncompressed_size: int | None = None,
) -> ContentStream:
    """Open a source payload as a read-only sequential byte stream.

    Args:
        source: String or path-like filesystem source. Plain files and the sole
            regular member of supported unencrypted archives are accepted.
        max_uncompressed_size: Optional inclusive payload-size limit in bytes.

    Returns:
        A package-owned :class:`ContentStream`. Closing it releases every
        source, archive, member, queue, and worker owned by the package.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: ``max_uncompressed_size`` is negative.
        InvalidArchiveError: A claimed archive cannot be opened.
        ArchiveStructureError: An archive violates the one-member policy.
        SizeLimitExceededError: A known payload size exceeds the limit.

    Errors that require decompression or terminal validation are raised by a
    later read rather than necessarily by this function.
    """

    _validate_max_uncompressed_size(max_uncompressed_size)
    path = normalize_source_path(source)
    source_format = detect_format(path)
    backend = open_backend(source_format, path)
    return ContentStream(
        backend,
        max_uncompressed_size=max_uncompressed_size,
    )


def scan_line_offsets(
    stream: BinaryIO,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> array:
    """Scan a caller-owned binary stream for LF-delimited line offsets.

    Args:
        stream: Readable binary stream consumed from its current position.
        skip_utf8_bom: Exclude an initial UTF-8 BOM from the first line when
            true. Offsets remain in the original byte space.
        buffer_size: Positive number of bytes requested per scan block.

    Returns:
        An ``array('Q')`` of line starts followed by the EOF sentinel.

    Raises:
        TypeError: An option has the wrong type or the stream returns text.
        ValueError: ``buffer_size`` is not positive.

    The current stream position becomes local offset zero. Scanning advances
    the stream to EOF; it neither closes nor restores its original position.
    """

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
    """Open a source and build its completed byte-line index.

    Args:
        source: String or path-like filesystem source.
        skip_utf8_bom: Exclude an initial UTF-8 BOM from the first line when
            true without changing the underlying byte coordinate system.
        buffer_size: Positive number of bytes requested per scan block.
        max_uncompressed_size: Optional inclusive payload-size limit in bytes.

    Returns:
        An ``array('Q')`` of line starts followed by decompressed EOF.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: A numeric argument is outside its permitted range.
        ArchiveLineIndexError: Source, archive, extraction, size, or index
            validation fails.

    The package-created stream is always closed. No partial index is returned,
    and successful return includes terminal archive validation.
    """

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


def write_sqlite_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Atomically write offsets to a dedicated SQLite database.

    Args:
        offsets: Valid completed ``array('Q')`` offset sequence.
        destination: Filesystem path for the dedicated database.
        overwrite: Replace an existing destination only when true.

    Raises:
        FileExistsError: The destination exists and replacement is disabled.
        InvalidIndexError: ``offsets`` violates the index contract.
        PersistenceError: SQLite cannot create a valid database.

    A pre-publication failure preserves an existing destination.
    """

    _write_sqlite_index(offsets, destination, overwrite=overwrite)


def read_sqlite_index(source: str | PathLike[str]) -> array:
    """Load and validate a dedicated SQLite index database.

    Args:
        source: Filesystem path to the database.

    Returns:
        The validated offsets as ``array('Q')``.

    Raises:
        FileNotFoundError: ``source`` does not exist.
        InvalidIndexError: Stored offsets violate the index contract.
        PersistenceError: SQLite cannot read the database or execute its query.

    A noncanonical schema raises ``InvalidIndexError``.
    """

    return _read_sqlite_index(source)


def write_raw_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Atomically write offsets as headerless little-endian ``uint64`` values.

    Args:
        offsets: Valid completed ``array('Q')`` offset sequence.
        destination: Filesystem path for the raw index.
        overwrite: Replace an existing destination only when true.

    Raises:
        FileExistsError: The destination exists and replacement is disabled.
        InvalidIndexError: ``offsets`` violates the index contract.
        PersistenceError: The complete raw representation cannot be written.

    A pre-publication failure preserves an existing destination.
    """

    _write_raw_index(offsets, destination, overwrite=overwrite)


def read_raw_index(source: str | PathLike[str]) -> array:
    """Load and validate a headerless little-endian raw index.

    Args:
        source: Filesystem path to the raw index.

    Returns:
        The validated offsets as ``array('Q')``.

    Raises:
        FileNotFoundError: ``source`` does not exist.
        InvalidIndexError: The byte length or decoded offsets are invalid.
        OSError: The source cannot be read through ordinary filesystem I/O.
    """

    return _read_raw_index(source)


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
