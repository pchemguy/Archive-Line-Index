# Archive Line Index

Archive Line Index is a Python library for building compact byte-offset indexes of line-oriented data and reading source content as a sequential binary stream. An index records where each line starts and where the content ends, allowing consumers to identify line byte ranges without decoding text or retaining complete lines in memory. Streaming and index construction are independently usable.

Inputs are filesystem paths or caller-supplied blocking binary readers. Index construction returns an in-memory `array("Q")` of unsigned eight-byte offsets: one start per line, followed by an end-of-file sentinel. For example, `b"a\nb"` produces `[0, 2, 3]`, describing the byte ranges `[0, 2)` and `[2, 3)`. Streaming returns the original payload bytes through `read` or `readinto`.

The Python interfaces are imported from `archive_line_index`:

| Interface | Input | Output and ownership |
| --- | --- | --- |
| `open_content_stream` | Filesystem path (`str` or text path-like object) | Owned `ContentStream` for sequential binary reads; the caller closes it. |
| `scan_line_offsets` | Blocking binary reader with `read(size) -> bytes` | Completed offset array; the reader is borrowed and remains open. |
| `build_line_index` | Filesystem path (`str` or text path-like object) | Completed offset array; source opening and closure are managed by the library. |

The current 0.1.0 library requires Python 3.11 or later and supports plain files and caller-supplied binary readers. Planned capabilities include single-payload ZIP/TAR/7z archive inputs, independent SQLite/raw index readers and writers, and an importable single-target CLI that produces both `.sqlite3` and `.u64` index files. These capabilities are not available in this version.

The library preserves payload bytes. LF is the only line terminator, CRLF retains both bytes, and the final offset is an EOF sentinel. An optional initial UTF-8 BOM policy changes the first line's start to 3 while retaining coordinates in the original bytes. No text decoding or line-ending normalization occurs.

## Installation

From a checkout, build the native artifacts and install the wheel:

```bash
python -m pip install build
python -m build
python -m pip install dist/archive_line_index-0.1.0-py3-none-any.whl
```

The source distribution is `dist/archive_line_index-0.1.0.tar.gz` and can independently rebuild the wheel. The declared runtime dependency is py7zr; development tools and separate archive executables are not required to use the installed library. Archive support is delivered in later versions.

## Stream without indexing

`open_content_stream` returns an owned, readable, nonseekable `ContentStream`. Use a context manager or call `close`. Short nonempty reads are legal; zero-length reads do not establish EOF. `readinto` measures capacity in bytes and leaves unused storage unchanged.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import open_content_stream

with TemporaryDirectory() as directory:
    target = Path(directory) / "payload.bin"
    target.write_bytes(b"a\nb")
    with open_content_stream(target, max_uncompressed_size=3) as stream:
        assert stream.read(2) == b"a\n"
        buffer = bytearray(b"????")
        assert stream.readinto(buffer) == 1
        assert buffer == b"b???"
        assert stream.read() == b""
    assert stream.closed
```

The inclusive size limit counts all payload bytes, including a BOM. Exactly-at-limit content still requires terminal validation. A read failure is retained until explicit closure; later otherwise-valid reads raise it rather than reporting EOF. Filesystem errors retain their ordinary Python types, and package-domain failures derive from `ArchiveLineIndexError`.

## Scan a borrowed binary reader

`scan_line_offsets` consumes from the reader's current position, defines that position as local offset zero and neither closes nor restores the reader. It needs only a blocking `read(size) -> bytes` operation; nonempty short reads are supported.

```python
from io import BytesIO

from archive_line_index import scan_line_offsets

payload = b"\xef\xbb\xbfalpha\r\n\nomega"
source = BytesIO(payload)
offsets = scan_line_offsets(source, buffer_size=2)
assert offsets.typecode == "Q" and offsets.itemsize == 8
assert offsets.tolist() == [3, 10, 11, 16]
assert len(offsets) - 1 == 3
assert payload[offsets[0]:offsets[1]] == b"alpha\r\n"
assert not source.closed
```

Set `skip_utf8_bom=False` to include the initial BOM in first-line content. Later or incomplete BOMs remain ordinary bytes. Empty input yields `[0]`, skipped BOM-only input yields `[3]`, and a trailing LF adds no extra empty line. Line i spans `[offsets[i], offsets[i + 1])`.

## Build from a filesystem source

`build_line_index` opens and owns the content stream, scans through validated EOF and closes it on success or failure. It returns only the completed array; it creates no output files.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import build_line_index

with TemporaryDirectory() as directory:
    target = Path(directory) / "records.txt"
    target.write_bytes(b"alpha\r\n\nomega")
    offsets = build_line_index(
        target, buffer_size=4, max_uncompressed_size=13
    )
    assert offsets.tolist() == [0, 7, 8, 13]
```

Sources are strings or path-like objects returning strings. Bytes paths are rejected; URL fetching is not supported. Recognized archive signatures/suffixes raise `UnsupportedFormatError` until their adapters are delivered; they are never silently treated as plain content. Sources must remain stable during an operation, and callers serialize operations on each stream.

## Memory and failure behavior

The default scanner buffer is 1 MiB. Working payload storage is bounded by the current block and at most three BOM-probe bytes; no complete line is assembled. The offset array grows by eight bytes per line start plus the EOF sentinel, excluding object/allocation overhead. Offsets lie in `0..2^63 - 1`. Streaming alone has no indexing-range restriction.

Calling `read()` with a negative size explicitly materializes all remaining content. Use bounded reads or `readinto` for incremental consumption. Allocation, source-read and terminal-validation failures return no partial index; an unbounded read that fails late returns no partial result from that call. Owned cleanup preserves a primary exception and attaches cleanup failures; close can be retried after failed resource release.

## Development and artifact verification

Install the configured development/test groups, then run checks from the root:

```bash
python -m pip install '.[dev,test]'
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m mypy
python -m pytest --cov=archive_line_index --cov-report=term-missing
python -m build
python scripts/check_release_artifacts.py --dist dist --tag v0.1.0 --write-checksums
python scripts/check_release_artifacts.py --dist dist --tag v0.1.0
```

Use a clean `dist` directory for the native source/wheel pair and generated `SHA256SUMS`. The checker verifies names/tag/embedded metadata, safe contents, source/wheel package equality and checksums; it does not publish a release. Installed integration tests build both artifacts, independently rebuild from the source distribution, and exercise clean runtimes outside the checkout. If mypy's native parser fails during container process discovery, `python -m mypy --no-native-parser` retains strict checking with its supported Python parser.

The [public API design](docs/dev/decomposition/public-api.md) and [contracts](docs/dev/SPEC.md) define the complete intended system. [Project brief](docs/dev/PROJECT.md), [architecture](docs/dev/ARCHITECTURE.md), [delivery plan](docs/dev/PLAN.md) and [implementation tasks](docs/dev/TASKS.md) describe scope and delivery. Development uses [SDD Manager](SDD-MANAGER.md); see the [AI-assisted development disclosure](AI_DISCLOSURE.md).
