# Public API design

## Ownership and consumers

This document owns the public surface defined by [DECOMPOSITION](../DECOMPOSITION.md). External Python callers import library operations from `archive_stream` and the CLI callable from `archive_stream.cli`. Backend classes, internal messages, format detection and filesystem helpers are not public exports. The declarations below are design signatures, not implementation code; postponed annotations support Python 3.11.

## Input types and defaults

```python
from __future__ import annotations

from array import array
from os import PathLike
from types import TracebackType
from typing import Protocol, TypeAlias

Source: TypeAlias = str | PathLike[str]
DEFAULT_BUFFER_SIZE: int


class ReadableBinary(Protocol):
    def read(self, size: int = -1, /) -> bytes: ...
```

`Source` is the path input for payload opening and persistence. `ReadableBinary` is the minimal scanner input; callers need only a blocking binary `read` operation, not positioning, a file descriptor or context-manager support. Standard binary files and `ContentStream` satisfy that interface. SPEC assigns the default buffer size and precise read-result validation.

## Content access

```python
def open_content_stream(
    source: Source,
    *,
    max_uncompressed_size: int | None = None,
) -> ContentStream: ...


class ContentStream:
    @property
    def closed(self) -> bool: ...

    def read(self, size: int = -1, /) -> bytes: ...
    def readinto(self, buffer: object, /) -> int: ...
    def readable(self) -> bool: ...
    def writable(self) -> bool: ...
    def seekable(self) -> bool: ...
    def seek(self, offset: int, whence: int = 0, /) -> int: ...
    def tell(self) -> int: ...
    def write(self, data: object, /) -> int: ...
    def close(self) -> None: ...
    def __enter__(self) -> ContentStream: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
```

`open_content_stream` is the supported constructor; exposing the stream type does not expose a backend-taking constructor. The returned object owns its backend and is explicitly closeable and context-managed. Its supported payload operations are `read` and `readinto`; `readinto` accepts a writable contiguous byte buffer through Python's buffer protocol. The broad `object` annotation permits arbitrary buffer providers without adding a runtime typing dependency.

`readable`, `writable` and `seekable` describe capabilities. `seek`, `tell` and `write` are rejection surfaces that raise `io.UnsupportedOperation`, not optional implementations. No full `BinaryIO` implementation, iteration API or random access is promised by the type. SPEC defines validation, closed-state precedence and exact zero-length/unbounded-read behavior.

## Index construction

```python
def scan_line_offsets(
    stream: ReadableBinary,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> array[int]: ...


def build_line_index(
    source: Source,
    *,
    skip_utf8_bom: bool = True,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
    max_uncompressed_size: int | None = None,
) -> array[int]: ...
```

The concrete returned representation is the canonical unsigned offset array in DECOMPOSITION. Direct scanning borrows the stream from its current position and defines that position as local byte offset zero. Source-based building owns and closes the stream it opens. Neither operation returns a partial index after a failure.

## Persistence

```python
def write_sqlite_index(
    offsets: array[int], destination: Source, *, overwrite: bool = False
) -> None: ...


def read_sqlite_index(source: Source) -> array[int]: ...


def write_raw_index(
    offsets: array[int], destination: Source, *, overwrite: bool = False
) -> None: ...


def read_raw_index(source: Source) -> array[int]: ...
```

Each persistence operation is independent. Writers borrow a canonical array for the call; readers return a newly owned canonical array. All persistence handles and temporary files are package-owned. Destinations are explicit arguments, and `overwrite` selects protected creation versus authorized replacement. SPEC defines the dedicated SQLite schema, exact raw encoding and publication/cleanup error behavior.

## CLI entry points

```python
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int: ...
```

`archive_stream.cli.main` is a public submodule entry point. `None` selects command arguments from `sys.argv[1:]`; an explicit sequence supports in-process callers. The adapter returns a status for normal success, help, command errors and expected operational failures instead of raising `SystemExit`. It performs no parsing, I/O or process exit at import time. SPEC owns invocation syntax, destination selection, messages and status codes.

The installed console entry is `archive-line-index = "archive_stream.cli:main"`. Module execution through `python -m archive_stream` invokes that same callable and converts its return value into process exit status. Importing `archive_stream.__main__` also has no execution side effect; the executable wrapper is guarded. No root-level `main` re-export or general CLI framework is part of the surface.

## Public errors and exports

```python
class ArchiveLineIndexError(Exception): ...

class UnsupportedFormatError(ArchiveLineIndexError): ...
class InvalidArchiveError(ArchiveLineIndexError): ...
class ArchiveStructureError(ArchiveLineIndexError): ...
class SizeLimitExceededError(ArchiveLineIndexError): ...
class ExtractionError(ArchiveLineIndexError): ...
class InvalidIndexError(ArchiveLineIndexError): ...
class PersistenceError(ArchiveLineIndexError): ...
```

The error component owns these classes. Their categories respectively cover unsupported formats, malformed recognized archives, invalid member structure, size-limit violations, extraction/delivery failures, invalid offset representations and persistence-engine failures. Specific ordinary Python exceptions remain available where appropriate; SPEC owns the complete classification and precedence.

The package-root export set is exactly `Source`, `ReadableBinary`, `DEFAULT_BUFFER_SIZE`, `ContentStream`, `open_content_stream`, `scan_line_offsets`, `build_line_index`, the four persistence functions and the listed exception classes. Consumers are not given public backend registration, worker controls, format enums, temporary-file helpers or a combined multi-output writer.

## Progress logging surface

Index construction emits INFO through archive_stream.scanner, with one-second chunk-boundary observations of complete-buffer capacity in rounded binary units and an exact final validated byte count. Library callers opt in using standard logging configuration; no callback, constructor parameter or new root export is introduced. Direct scanning still borrows its reader; build_line_index still owns source cleanup. The CLI adds case-insensitive --log-level with INFO default and WARNING-or-higher suppression, preserving stdout summaries and exception/status ownership. [Progress contract](../spec/progress-logging.md) owns counts, timing, configuration restoration and the intentional informational stderr output.
