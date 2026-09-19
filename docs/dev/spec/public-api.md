# Public API specification

## 1. Scope

This specification defines the supported Python import surface, function and class contracts visible to callers, shared argument validation, and public error model. Component-specific behavior remains canonical in the linked content-stream, archive-handling, line-index, and persistence specifications.

The distribution name is `archive-line-index`; the import package is `archive_line_index`.

## 2. Supported runtime

- Minimum Python version: 3.11.
- Supported operating systems: Windows, Linux, and macOS.
- The package is synchronous. An `asyncio` API is outside scope.
- `py7zr` is the only required third-party runtime dependency.
- Project metadata shall constrain `py7zr` to a tested compatible release range; determining and verifying that range is an implementation-plan task.
- No installed archive executable is required.

## 3. Public source type and constants

```python
from os import PathLike
from typing import BinaryIO, TypeAlias

Source: TypeAlias = str | PathLike[str] | BinaryIO

DEFAULT_BUFFER_SIZE = 1024 * 1024
```

`DEFAULT_BUFFER_SIZE` is one mebibyte and is used by the public scanning operations. Archive libraries may have additional internal buffering. The 7z producer queue capacity is an internal constant and is not public API.

## 4. Content-stream API

```python
def open_content_stream(
    source: Source,
    *,
    max_uncompressed_size: int | None = None,
) -> ContentStream:
    """Open the plain payload or sole archive member as decompressed bytes."""
```

`open_content_stream()` returns an already initialized, context-managed, read-only sequential binary stream. Format and structural errors that can be detected without consuming member content may be raised by this call. Errors that require continued decompression or terminal validation are raised by a later read.

`ContentStream` is public and implements the readable binary-I/O operations needed by `BinaryIO`, including:

```python
class ContentStream:
    def readable(self) -> bool: ...       # True while open
    def writable(self) -> bool: ...       # False
    def seekable(self) -> bool: ...       # False
    def read(self, size: int = -1) -> bytes: ...
    def readinto(self, buffer) -> int: ...
    def close(self) -> None: ...
    def __enter__(self) -> ContentStream: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
```

Unsupported positioning or mutation operations raise `io.UnsupportedOperation`. Operations requiring an open stream follow normal Python I/O behavior and raise `ValueError` after closure. `close()` is idempotent.

The complete stream contract is defined in [content-stream.md](content-stream.md).

## 5. Index-building API

### 5.1 Scan an existing binary stream

```python
def scan_line_offsets(
    stream: BinaryIO,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> array:
    """Return line starts followed by an EOF sentinel."""
```

This function consumes from the stream's current position through terminal EOF. Offsets are relative to that starting position, which becomes offset zero for the scan. It neither closes the caller's stream nor restores its position.

When the stream is a `ContentStream`, successful return also proves terminal archive validation. For an arbitrary caller stream, successful return proves only successful reading through its reported EOF.

### 5.2 Open a source and build an index

```python
def build_line_index(
    source: Source,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
    max_uncompressed_size: int | None = None,
) -> array:
    """Open a source, scan its payload, and return a completed offset array."""
```

This is the composition of `open_content_stream()` and `scan_line_offsets()`. It always closes the package-created `ContentStream`, including when scanning fails. Caller-provided source ownership remains unchanged.

Both functions return `array("Q")`. They return no partial result following an exception.

Detailed semantics are defined in [line-index.md](line-index.md).

## 6. Persistence API

Persistence is explicit and separate from index construction. No operation implicitly derives an output path from the input archive.

### 6.1 SQLite

```python
def write_sqlite_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Write a complete offset sequence to a dedicated SQLite file."""


def read_sqlite_index(
    source: str | PathLike[str],
) -> array:
    """Load and validate offsets from a dedicated SQLite index file."""
```

### 6.2 Raw binary

```python
def write_raw_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Write offsets as headerless little-endian uint64 values."""


def read_raw_index(
    source: str | PathLike[str],
) -> array:
    """Load and validate a complete raw offset file."""
```

Writes accept only filesystem destinations because safe publication requires a temporary sibling and atomic replacement. Reads likewise accept paths so that the whole persistence lifecycle has one ownership model.

If the destination exists and `overwrite=False`, the write raises `FileExistsError` without modifying it. With `overwrite=True`, the writer builds and validates a temporary sibling, then atomically replaces the destination. A failure before replacement leaves the prior destination intact.

SQLite and raw writes are independent. The package provides no cross-file transaction or combined two-destination write operation.

The complete format contracts are defined in [persistence.md](persistence.md).

## 7. Argument validation

Validation that does not require source I/O occurs before opening a path, starting a worker, creating a temporary file, or modifying a destination.

- `buffer_size` must be an integer greater than zero; `bool` is rejected.
- `max_uncompressed_size` must be `None` or a non-negative integer; `bool` is rejected.
- `skip_utf8_bom` and `overwrite` must be actual `bool` values.
- A source stream must provide binary bytes rather than text strings.
- Persistence input must be an `array` with type code `"Q"` and 8-byte items.
- Offset arrays must contain at least one value, fit the shared signed SQLite range, and satisfy the monotonic/sentinel structural contract.
- Path-like arguments are resolved through normal Python filesystem semantics; empty or otherwise invalid paths fail through the corresponding standard exception.

Invalid public values raise `TypeError` when the argument has the wrong kind and `ValueError` when it has the correct kind but an invalid value. This policy is applied consistently; booleans are not silently accepted as integers.

## 8. Ownership and positioning

For source paths, the package owns every opened file and archive object. For a caller-provided `BinaryIO`, the caller retains ownership and the package shall not close it.

Processing begins at the caller stream's current position. That position is not restored. `scan_line_offsets()` defines its returned offset zero at the current position when scanning begins. `open_content_stream()` applies format detection from the current position and replays any detection prefix required for plain non-seekable input.

Persistence read functions own and close the files they open. Persistence write functions own their temporary and destination handles but not the supplied in-memory array.

## 9. Public exceptions

```python
class ArchiveLineIndexError(Exception): ...

class UnsupportedFormatError(ArchiveLineIndexError): ...
class InvalidArchiveError(ArchiveLineIndexError): ...
class ArchiveStructureError(ArchiveLineIndexError): ...
class EncryptedArchiveError(ArchiveLineIndexError): ...
class SizeLimitExceededError(ArchiveLineIndexError): ...
class ExtractionError(ArchiveLineIndexError): ...
class InvalidIndexError(ArchiveLineIndexError): ...
class PersistenceError(ArchiveLineIndexError): ...
```

Meanings:

- `UnsupportedFormatError`: the content is a recognized but unsupported archive/compression format.
- `InvalidArchiveError`: a claimed or signature-recognized supported archive is malformed or cannot be opened as that format.
- `ArchiveStructureError`: archive entries violate the exactly-one-regular-file structure policy.
- `EncryptedArchiveError`: archive or selected member requires decryption.
- `SizeLimitExceededError`: declared or actual decompressed bytes exceed the configured limit.
- `ExtractionError`: decompression, CRC, footer, or backend delivery fails without a narrower public classification.
- `InvalidIndexError`: an in-memory or persisted offset sequence violates its structural or binary-format contract.
- `PersistenceError`: SQLite or raw persistence fails without a more appropriate ordinary Python exception.

Backend and persistence failures are translated to the narrowest applicable public exception and retain their original cause with exception chaining.

The following ordinary exceptions retain their normal types:

- `FileNotFoundError` for a missing source or persistence input;
- `FileExistsError` for a protected existing destination;
- `PermissionError` and other specific `OSError` subclasses;
- `TypeError` and `ValueError` for public argument validation;
- `io.UnsupportedOperation` for unsupported stream operations;
- `MemoryError` if the requested in-memory index cannot be allocated.

An exception raised by a 7z worker is transported to and raised by the consumer-facing operation. Caller-requested early close is not surfaced as an extraction failure.

## 10. Package exports

`archive_line_index.__init__` re-exports only:

- `Source`;
- `DEFAULT_BUFFER_SIZE`;
- `ContentStream`;
- `open_content_stream`;
- `scan_line_offsets`;
- `build_line_index`;
- `write_sqlite_index` and `read_sqlite_index`;
- `write_raw_index` and `read_raw_index`;
- the public exception hierarchy.

Backend classes, detector state, queue messages, source wrappers, offset validation helpers, temporary-file helpers, and archive-library objects are internal and receive no compatibility guarantee.

## 11. Public API acceptance conditions

The public API conforms when:

1. Every documented export is importable from `archive_line_index` in an installed wheel.
2. No undocumented backend or persistence implementation name is re-exported.
3. Invalid arguments fail before resource acquisition or destination mutation.
4. Path sources and caller-owned streams obey their respective ownership rules.
5. Direct stream scanning and source-based index building produce identical offsets for equivalent bytes.
6. Persistence functions protect existing destinations by default and preserve them after failed explicit replacement.
7. Narrow public errors are stable across backend-specific exception changes, with original causes retained.
