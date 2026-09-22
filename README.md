# Archive Line Index

Archive Line Index is a synchronous Python library for streaming one byte-oriented payload from a filesystem path and indexing its LF-delimited lines. The payload can be a plain file or the sole regular-file member of an unencrypted ZIP, TAR, compressed TAR, or 7z archive.

The package exposes decompressed bytes without extracting a member to disk. It can build an in-memory `array("Q")` of line offsets and persist that same offset sequence in SQLite or as headerless little-endian unsigned 64-bit integers.

## Installation

Archive Line Index requires Python 3.11 or later. Install it with `python -m pip install archive-line-index`. The only third-party runtime dependency is `py7zr`; ZIP and TAR support use the Python standard library.

## Stream content

`open_content_stream()` returns a read-only, non-seekable `ContentStream`. Bounded reads keep memory use independent of the decompressed payload size.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import open_content_stream

with TemporaryDirectory() as directory:
    source = Path(directory) / "events.jsonl"
    source.write_bytes(b'{"id": 1}\n{"id": 2}\n')

    chunks = []
    with open_content_stream(source) as stream:
        while chunk := stream.read(8):
            chunks.append(chunk)

    assert b"".join(chunks) == source.read_bytes()
```

An optional `max_uncompressed_size` argument rejects content that exceeds a caller-selected byte limit. Avoid an unbounded `read()` when the expanded size is not already known; it necessarily materializes all remaining bytes.

## Build an in-memory index

`build_line_index()` opens a supported source, reads it through terminal EOF, and returns unsigned 64-bit offsets. `scan_line_offsets()` provides the same scanner for an already open binary stream.

```python
from array import array
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import build_line_index

with TemporaryDirectory() as directory:
    source = Path(directory) / "records.txt"
    source.write_bytes(b"alpha\nbeta\n")

    offsets = build_line_index(source)
    assert offsets == array("Q", [0, 6, 11])
```

Each line-start offset is measured in the decompressed byte stream. The final and greatest value is always the EOF sentinel, not another line. Thus the example has two lines starting at `0` and `6`, followed by decompressed EOF at `11`; a trailing LF does not create an extra empty line. By default an initial UTF-8 BOM is excluded from the first line, which can be changed with `skip_utf8_bom=False`.

## Persist an index

Persistence is explicit and independent of the source. Writers refuse to replace an existing destination unless `overwrite=True`; readers return a validated `array("Q")`.

```python
from array import array
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import (
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)

offsets = array("Q", [0, 6, 11])
with TemporaryDirectory() as directory:
    sqlite_path = Path(directory) / "records.sqlite"
    raw_path = Path(directory) / "records.u64"

    write_sqlite_index(offsets, sqlite_path)
    write_raw_index(offsets, raw_path)

    assert read_sqlite_index(sqlite_path) == offsets
    assert read_raw_index(raw_path) == offsets
```

The SQLite representation is a dedicated database with one ordered offset per row. The raw representation contains only consecutive little-endian `uint64` values, including the EOF sentinel.

## Ownership and integrity

A `ContentStream` owns and closes every source file, archive object, and member handle it opens. Its context manager provides deterministic cleanup, including cancellation of active 7z extraction. In contrast, `scan_line_offsets()` does not close a caller-supplied stream.

Archive integrity is established only after all backend completion work succeeds. A successful terminal EOF (`b""`) means the selected member was fully consumed and all available trailing checks completed. Closing early is safe and deterministic, but makes no claim about the integrity of unread archive data.

## Limits and non-goals

Index entries are decompressed byte offsets, not positions in the compressed archive. Neither `ContentStream` nor an index supports random seek into compressed data. The package also intentionally does not provide:

- text decoding, newline normalization, or record-format validation;
- archive or source identity, fingerprints, metadata, or stale-index checks;
- memory mapping of raw indexes;
- encrypted archives, passwords, or credential discovery;
- extracted member files or automatic index naming;
- a command-line interface.

## Development documents

The normative behavior is defined by the [SPEC](docs/dev/SPEC.md), its ordered implementation is described by the [PLAN](docs/dev/PLAN.md), and physical code ownership is mapped in the [LAYOUT](docs/dev/layout.md).
