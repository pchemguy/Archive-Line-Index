# Archive Line Index

Archive Line Index is a Python library and minimal CLI for building compact byte-offset indexes of line-oriented data, streaming source bytes, and storing or reloading indexes in SQLite or raw binary form. An index records where each line starts and where the content ends, allowing consumers to identify line byte ranges without decoding text or retaining complete lines in memory. Streaming, indexing and persistence are independently usable.

Payload inputs are filesystem paths or caller-supplied blocking binary readers. Python index construction returns an in-memory `array("Q")` of unsigned eight-byte offsets: one start per line, followed by an end-of-file sentinel. For example, `b"a\nb"` produces `[0, 2, 3]`, describing the byte ranges `[0, 2)` and `[2, 3)`. Streaming returns original payload bytes through `read` or `readinto`. Persistence stores the completed array at an explicit path; the CLI indexes one target once and writes both `.sqlite3` and `.u64` files.

Library functions are imported from `archive_line_index`; the importable CLI callable is `archive_line_index.cli.main`.

| Interface | Input | Output and ownership |
| --- | --- | --- |
| `open_content_stream` | Filesystem path (`str` or text path-like object) | Owned `ContentStream` for sequential binary reads; the caller closes it. |
| `scan_line_offsets` | Blocking binary reader with `read(size) -> bytes` | Completed offset array; the reader is borrowed and remains open. |
| `build_line_index` | Filesystem path | Completed offset array; source opening and closure are managed by the library. |
| `write_sqlite_index`, `write_raw_index` | Completed offset array and explicit destination path | One complete index file; the input array is borrowed and unchanged. |
| `read_sqlite_index`, `read_raw_index` | Stored index path | A newly owned, validated offset array; no payload source is needed. |
| `cli.main` / console / module | One target and optional shared output stem/overwrite flag | Integer status and paired SQLite/raw files from one scan. |

The library requires Python 3.11 or later and supports plain payload files, single-payload ZIP, TAR (plain/gzip/bzip2/xz) and 7z archives, caller-supplied binary readers, both persistence formats and all three CLI invocation forms.

The library preserves payload bytes. LF is the only line terminator, CRLF retains both bytes, and the final offset is an EOF sentinel. An optional initial UTF-8 BOM policy changes the first line's start to 3 while retaining coordinates in the original bytes. No text decoding or line-ending normalization occurs.

## Installation

GitHub releases provide a [wheel bundle](https://github.com/pchemguy/Archive-Line-Index/releases/latest/download/archive-line-index-wheel.zip), [source bundle](https://github.com/pchemguy/Archive-Line-Index/releases/latest/download/archive-line-index-source.zip) and [SHA256SUMS](https://github.com/pchemguy/Archive-Line-Index/releases/latest/download/SHA256SUMS). Verify the downloaded bundle against SHA256SUMS, then extract and install its native package:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.4.0-py3-none-any.whl
```

Each hosted bundle has a stable version-free name. The wheel bundle contains one ecosystem-valid wheel; the source bundle contains one source distribution, `archive_line_index-0.4.0.tar.gz`, which independently rebuilds that wheel. Version identity remains in package metadata, internal native filenames and the release tag. The links above refer to the latest published release; use its tag-specific assets and included package version when installing a pinned release.

From a checkout, build private native package inputs with `python -m build`. The declared runtime dependency is `py7zr>=1.1.4,<1.2`, tested with 1.1.4; development tools and separate archive executables are not required for installed use. ZIP and plain/gzip/bzip2/xz TAR use the Python standard library. The 7z dependency is loaded only when opening 7z content.

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

## Line-boundary scanning

`scan_line_offsets` reads bounded byte blocks (1 MiB by default) and searches each block with repeated `bytes.find` calls. The core loop in [`scanner.py`](src/archive_line_index/scanner.py), shown below as an implementation excerpt, records the byte immediately after each LF; `position` is the block’s starting offset:

```py
start = 0
while (newline := block.find(b"\n", start)) >= 0:
    append_offset(offsets, position + newline + 1)
    start = newline + 1
```

This keeps byte searching in the runtime’s native `bytes` implementation, with Python work per match rather than per byte, and never assembles a complete line. A one-byte LF needs no overlap between blocks; BOM handling and the final EOF sentinel are managed outside this loop. Python byte-by-byte iteration adds interpreter work, `readline()`/`split()` materialize lines or fragments, and `mmap` requires a suitable file rather than the generic binary-reader interface. Blockwise `bytes.find` fits the bounded-memory streaming contract without an extra scanning dependency.

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

Sources are strings or path-like objects returning strings. Bytes paths are rejected; URL fetching is not supported. Recognized archive signatures or suffixes select the corresponding adapter; archive claims never silently fall back to plain content. Sources must remain stable during an operation, and callers serialize operations on each stream.

## Index a ZIP payload

ZIP archives must contain exactly one regular file, optionally nested under directories. Empty payloads are valid; directory entries are ignored, while extra files (including metadata files), links and other special entries are rejected. Member names are never extracted to filesystem paths. Detected encryption and unavailable codecs are unsupported; malformed archives and payload integrity failures retain distinct error categories. Member CRC validation and agreement between delivered bytes and the declared member size must complete before indexing succeeds. These checks use the member stream exposed by the standard library.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from archive_line_index import build_line_index

with TemporaryDirectory() as directory:
    target = Path(directory) / "records.zip"
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("nested/records.txt", b"alpha\nbeta")
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

The CLI accepts the same archive target and persists offsets in the uncompressed payload's byte coordinates. For `records.zip`, its default outputs are `records.sqlite3` and `records.u64` beside the archive. Signature evidence takes precedence over a conflicting suffix, and invalid suffix-claimed ZIP input cannot fall back to plain bytes.

## Index a TAR payload

Plain TAR and gzip/bzip2/xz-compressed TAR follow the same sole-regular-file policy as ZIP. Accepted suffixes are `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz`, `.tbz2`, `.tar.xz` and `.txz`; supported signatures also identify unconventional filenames. Compressed data that is not TAR is rejected. Standard TAR extension headers are interpreted by the library rather than counted as payload files.

```python
import tarfile
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import build_line_index

with TemporaryDirectory() as directory:
    target = Path(directory) / "records.tar.gz"
    payload = b"alpha\nbeta"
    with tarfile.open(target, "w:gz") as archive:
        member = tarfile.TarInfo("nested/records.txt")
        member.size = len(payload)
        archive.addfile(member, BytesIO(payload))
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

TAR reads sequentially and validates entries after the selected payload before successful EOF. A later extra file or special entry invalidates the archive even after payload bytes were returned. Damaged later headers, incomplete end markers and non-padding trailing bytes fail validation. Compressed readers are drained through their available trailer/integrity checks; a corrupt footer cannot yield a completed index or CLI output pair. Early close releases resources without claiming terminal validation. For `records.tar.gz`, CLI defaults are `records.tar.sqlite3` and `records.tar.u64` beside the archive.

## Index a 7z payload

7z accepts exactly one regular file, including an empty or nested payload, and ignores directory entries. Extra files, links and special entries are rejected; encrypted archives and unavailable codecs raise `UnsupportedFormatError`. Extraction streams into a callback without creating member paths on disk. Metadata validation precedes delivery, and extraction, declared-size and available CRC checks must complete before an index or CLI outputs can be returned.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from py7zr import SevenZipFile

from archive_line_index import build_line_index

with TemporaryDirectory() as directory:
    target = Path(directory) / "records.7z"
    with SevenZipFile(target, "w") as archive:
        archive.writestr(b"alpha\nbeta", "nested/records.txt")
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

The [`7z adapter`](src/archive_line_index/backends/sevenzip.py) forwards callback data through a [`bounded producer bridge`](src/archive_line_index/backends/producer.py): one non-daemon worker, one queued block and one current consumer block, each at most 1 MiB. Callback buffers are subdivided before queueing. Dependency decompressor/callback allocations are outside those package buffer bounds. Closing cancels package waits and joins the worker; checks during package waits occur at most 0.05 seconds apart, but dependency operations can delay cancellation, so this is not a total close-latency guarantee. Early close does not assert integrity. For `records.7z`, CLI defaults are `records.sqlite3` and `records.u64` beside the archive.

## Store and reload an index independently

SQLite uses a dedicated rowid table `line_index(offset INTEGER PRIMARY KEY)`, with one row per offset including EOF. Raw files contain only consecutive little-endian unsigned 64-bit values, with no header. Both readers validate the complete representation before returning an array; neither requires the payload source.

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

with TemporaryDirectory() as directory:
    root = Path(directory)
    offsets = array("Q", [0, 2, 3])
    write_sqlite_index(offsets, root / "index.sqlite3")
    write_raw_index(offsets, root / "index.u64")
    assert read_sqlite_index(root / "index.sqlite3") == offsets
    assert read_raw_index(root / "index.u64") == offsets
```

Writers protect existing destinations by default, including dangling symlinks and names created at publication time. `overwrite=True` authorizes atomic replacement of the whole file; SQLite replacement also replaces any old unrelated tables. Each file is built and validated in an owned temporary sibling, closed and independently published. A failure before publication preserves the previous destination. A cleanup failure after publication retains the complete new file and reports that fact in an exception note. There is no cross-file transaction or rollback of an earlier completed publication.

## Index one target through the CLI

Given an existing `data/events.txt` and an existing `results` directory:

```bash
archive-line-index data/events.txt
python -m archive_line_index data/events.txt --output results/custom
archive-line-index data/events.txt --overwrite
archive-line-index -- -events.txt
```

The first command creates `data/events.sqlite3` and `data/events.u64`. Defaults use the input directory and remove only the final suffix: `events.tar.gz` would use stem `events.tar`, while an extensionless name or dotfile keeps its normal path stem. `--output results/custom` appends both extensions to that shared stem. Parent directories are not created automatically. Quote paths containing spaces; `--` permits a target beginning with a hyphen.

Both destinations are checked before scanning. An existing output requires `--overwrite`; any output alias of the input is rejected even with overwrite. The command scans once, writes SQLite first and raw second, and reports both paths and the line count only after both succeed. Help returns 0, usage errors 2, expected operational errors 1 and interruption 130. Diagnostics go to stderr and identify known completed outputs, including post-publication cleanup notes; a nonzero status does not imply both files are absent.

The same callable can be used without exiting the Python caller:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_line_index import read_raw_index, read_sqlite_index
from archive_line_index.cli import main

with TemporaryDirectory() as directory:
    root = Path(directory)
    target = root / "events.txt"
    target.write_bytes(b"a\nb")
    assert main([str(target)]) == 0
    assert read_sqlite_index(root / "events.sqlite3").tolist() == [0, 2, 3]
    assert read_raw_index(root / "events.u64").tolist() == [0, 2, 3]
    assert main([str(target), "--overwrite"]) == 0
    assert main([str(target), "--output", str(root / "custom")]) == 0
    assert read_sqlite_index(root / "custom.sqlite3") == read_raw_index(root / "custom.u64")
```

Importing the package, CLI or module runner performs no command execution. An explicit argv must be a sequence of strings; `None` uses process arguments. Library APIs continue to raise exceptions directly and do not acquire CLI printing or process-exit behavior.

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
python scripts/check_release_artifacts.py --dist dist --tag v0.4.0 --write-checksums
python scripts/check_release_artifacts.py --dist dist --tag v0.4.0
python -m scripts.prepare_release --native-dist dist --output release --tag v0.4.0
python -m scripts.prepare_release --output release --tag v0.4.0 --check
```

Use clean `dist` and `release` directories: `dist` contains private native build inputs, while `release` is the complete hosted inventory of wheel/source ZIP bundles and SHA256SUMS. The native checker verifies package/tag/metadata agreement, safe contents and source/wheel equality. The release checker independently rejects versions in every hosted filename, validates the bundled native pair and verifies outer checksums; neither command publishes a release. The actual naming gate is tested against the shared notation vectors, including historical and single-component versions with matching faulty expected names. Installed integration tests build both artifacts, independently rebuild from the source distribution, and exercise clean runtimes outside the checkout. If mypy's native parser fails during container process discovery, `python -m mypy --no-native-parser` retains strict checking with its supported Python parser.

The [public API design](docs/dev/decomposition/public-api.md) and [contracts](docs/dev/SPEC.md) define the complete intended system. [Project brief](docs/dev/PROJECT.md), [architecture](docs/dev/ARCHITECTURE.md), [delivery plan](docs/dev/PLAN.md) and [implementation tasks](docs/dev/TASKS.md) describe scope and delivery. Development uses [SDD Manager](SDD-MANAGER.md); see the [AI-assisted development disclosure](AI_DISCLOSURE.md).
