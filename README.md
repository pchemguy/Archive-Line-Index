# Archive Stream

Archive Stream transparently streams uncompressed files and compressed archive payloads through a single Python interface. Pass a path to `open_content_stream()` and read the original payload bytes in blocks. The library detects the format, selects the appropriate reader and decompressor automatically, and decompresses the payload on the fly.

Supported sources include plain files, ZIP, TAR (uncompressed or gzip-, bzip2-, or xz-compressed), and 7z. Each archive contains one regular-file payload, streamed without extracting a member file to disk.

For line-oriented data, the library can independently build, store, and reload a byte-offset index. The index records each LF-delimited line start and an end-of-file offset in the uncompressed payload. Python callers can build an index from a path or a caller-supplied blocking binary reader. The single-target CLI writes both SQLite and raw binary indexes. The library requires Python 3.11 or later.

## Installation

If the target environment has the previous `archive-line-index` distribution, uninstall it first with `python -m pip uninstall archive-line-index`. Both distributions register the `archive-line-index` console command. Update Python imports and module invocations to `archive_stream` and scanner logger configuration to `archive_stream.scanner`.

Download the [v0.5.2 wheel bundle](https://github.com/pchemguy/Archive-Stream/releases/download/v0.5.2/archive-stream-wheel.zip) and [SHA256SUMS](https://github.com/pchemguy/Archive-Stream/releases/download/v0.5.2/SHA256SUMS). Compare the bundle's SHA-256 with the manifest, then extract and install the wheel:

```bash
python -m zipfile -e archive-stream-wheel.zip .
python -m pip install archive_stream-0.5.2-py3-none-any.whl
```

The [source bundle](https://github.com/pchemguy/Archive-Stream/releases/download/v0.5.2/archive-stream-source.zip) contains the source distribution. To install directly from a repository checkout, run `python -m pip install .` at its root.

The [v0.5.1 release](https://github.com/pchemguy/Archive-Stream/releases/tag/v0.5.1) provides the previous distribution and its installation instructions.

The declared runtime dependency is `py7zr>=1.1.4,<1.2`, tested with 1.1.4; development tools and separate archive executables are not required for installed use. ZIP and plain/gzip/bzip2/xz TAR use the Python standard library. The 7z dependency is loaded only when opening 7z content.

## Integration contract

The Python stream and index builder both accept a filesystem path and select the source backend automatically. The index CLI uses the same source handling. Supported archives contain exactly one regular-file payload.

| Interface | Entry point | Result |
| --- | --- | --- |
| Python payload stream | `open_content_stream(source)` | A context-managed sequential stream with `read` and `readinto`. |
| Python line index | `build_line_index(source)` | A completed `array("Q")` of byte offsets. Package-root readers and writers load and store it independently. |
| Index CLI | `archive-line-index SOURCE` | Both SQLite and raw index files from one scan; exit status reports success or failure. |

The CLI also runs as `python -m archive_stream SOURCE` or through the importable `archive_stream.cli.main([source])`, which returns an integer status. Library calls raise exceptions; index construction creates no output files. Each persistence output is published independently.

Offsets refer to the original uncompressed payload bytes, not archive positions or decoded characters. LF ends a line; the EOF sentinel is included in both stored formats. Output naming, overwrite rules, BOM handling, validation and failure outcomes are defined by the linked contracts. A later persistence failure can leave an earlier output published; scan-complete logging alone does not certify output publication.

| Integration concern | Authoritative reference |
| --- | --- |
| Public Python imports, signatures and types; operation outcomes and exceptions | [API signatures](docs/dev/decomposition/public-api.md) and [operation/error contract](docs/dev/spec/public-api.md) |
| Block reads, size limits, EOF and resource ownership | [Content stream contract](docs/dev/spec/content-stream.md) |
| CLI arguments, default paths, stdout/stderr and status codes | [CLI contract](docs/dev/spec/cli.md) |
| Offset representation, line ranges, BOM, EOF and bounds | [Line-index contract](docs/dev/spec/line-index.md) |
| SQLite schema, raw binary encoding, readers/writers and publication guarantees | [Persistence contract](docs/dev/spec/persistence.md) |
| Accepted source formats, automatic detection and archive restrictions | [Source/archive contract](docs/dev/spec/archive-handling.md) |
| Progress records, verbosity and application logging configuration | [Progress-logging contract](docs/dev/spec/progress-logging.md) |

## Stream a payload

`open_content_stream` returns an owned, readable, nonseekable `ContentStream`. Use a context manager or call `close`. For block processing, call `read(block_size)` with a positive size until it returns `b""`. A short nonempty block is valid. Use `readinto` to reuse a buffer. It measures capacity in bytes and leaves unused storage unchanged. The example creates a small compressed ZIP fixture and hashes its payload incrementally.

```python
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from archive_stream import open_content_stream

with TemporaryDirectory() as directory:
    target = Path(directory) / "payload.zip"
    payload = b"a\nb"
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("payload.bin", payload)

    digest = sha256()
    with open_content_stream(target, max_uncompressed_size=3) as stream:
        while block := stream.read(2):
            digest.update(block)
    assert digest.digest() == sha256(payload).digest()
```

The inclusive size limit counts all payload bytes, including a BOM. Exactly-at-limit content still requires terminal validation. A read failure is retained until explicit closure; later otherwise-valid reads raise it rather than reporting EOF. Filesystem errors retain their ordinary Python types, and package-domain failures derive from `ArchiveLineIndexError`.

Archive integrity errors can surface after some bytes have already been delivered. If downstream results require a valid complete archive, publish them after the stream reaches validated EOF. The application owns record parsing and any worker coordination or shared-memory transport.

## Index a source through the library

For an existing source, call `build_line_index(source)`; the same call handles a plain file or supported archive. Persist its result with the package-root writers when files are needed. The self-contained example below creates a small plain source, builds its index and writes/reloads both outputs.

`build_line_index` opens its own content stream, scans through validated EOF, and closes it on success or failure. Opening the source separately to process its bytes makes a separate pass through the payload. The completed index can be stored and reloaded independently. Its offsets describe line ranges without changing the stream's sequential access.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_stream import (
    build_line_index,
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)

with TemporaryDirectory() as directory:
    target = Path(directory) / "records.txt"
    target.write_bytes(b"alpha\r\n\nomega")
    offsets = build_line_index(
        target, buffer_size=4, max_uncompressed_size=13
    )
    assert offsets.tolist() == [0, 7, 8, 13]
    write_sqlite_index(offsets, Path(directory) / "records.sqlite3")
    write_raw_index(offsets, Path(directory) / "records.u64")
    assert read_sqlite_index(Path(directory) / "records.sqlite3") == offsets
    assert read_raw_index(Path(directory) / "records.u64") == offsets
```

The library owns source validation and closure and returns no partial array on failure. Writer destinations are explicit; existing files are protected unless `overwrite=True`. Each file is published independently, so a later failure can leave an earlier output complete.

### Store and reload an index independently

SQLite uses a dedicated rowid table `line_index(offset INTEGER PRIMARY KEY)`, with one row per offset including EOF. Raw files contain only consecutive little-endian unsigned 64-bit values, with no header. Both readers validate the complete representation before returning an array; neither requires the payload source.

```python
from array import array
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_stream import (
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
python -m archive_stream data/events.txt --output results/custom
archive-line-index data/events.txt --overwrite
archive-line-index data/events.txt --overwrite --log-level WARNING
archive-line-index -- -events.txt
```

The first command creates `data/events.sqlite3` and `data/events.u64`. Defaults use the input directory and remove only the final suffix: `events.tar.gz` would use stem `events.tar`, while an extensionless name or dotfile keeps its normal path stem. `--output results/custom` appends both extensions to that shared stem. Parent directories are not created automatically. Quote paths containing spaces; `--` permits a target beginning with a hyphen.

Both destinations are checked before scanning. An existing output requires `--overwrite`; any output alias of the input is rejected even with overwrite. The command scans once, writes SQLite first and raw second, and reports both paths and the line count only after both succeed. Help returns 0, usage errors 2, expected operational errors 1 and interruption 130. Diagnostics go to stderr and identify known completed outputs, including post-publication cleanup notes; a nonzero status does not imply both files are absent.

The same callable can be used without exiting the Python caller:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_stream import read_raw_index, read_sqlite_index
from archive_stream.cli import main

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

## Alphanum demo

Run either command from the checkout root in Windows CMD. Both demos load Archive Stream from `src` without installing it. The selected Python needs `py7zr>=1.1.4,<1.2` for the 7z fixture.

```bat
docs\demo\alphanum\demo_cli.bat
docs\demo\alphanum\demo_api.bat
```

The CLI and Python API demos index the same three-line payload as plain text, ZIP, TGZ, TBZ, TAR and 7z. Each writes `demo.sqlite3` and `demo.u64` beside each input in [the demo directory](https://github.com/pchemguy/Archive-Stream/tree/main/docs/demo/alphanum). Remove the generated indexes before rerunning either demo.

## Source backends

Sources are strings or path-like objects returning strings. Bytes paths are rejected; URL fetching is not supported. Recognized archive signatures or suffixes select the corresponding adapter; archive claims never silently fall back to plain content. Sources must remain stable during an operation, and callers serialize operations on each stream.

Archives contain exactly one regular-file payload, which may be empty or nested under directories. Directory entries are ignored; additional files (including metadata files), links and special entries are rejected. Member names are never extracted to filesystem paths. Early close releases resources without claiming terminal integrity validation.

Gzip, bzip2, and xz inputs must contain a TAR archive. The same `open_content_stream(source)` call handles all supported formats. The format-specific examples below illustrate index construction and create their own fixtures with `zipfile`, `tarfile`, or `py7zr`.

### Plain files

Plain files expose their original bytes through the same [stream API](#stream-a-payload). The [indexing example](#index-a-source-through-the-library) uses a plain file.

### ZIP

ZIP rejects detected encryption and unavailable codecs; malformed archives and payload integrity failures retain distinct error categories. Member CRC validation and agreement between delivered bytes and the declared member size must complete before indexing succeeds. These checks use the member stream exposed by the standard library.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from archive_stream import build_line_index

with TemporaryDirectory() as directory:
    # Fixture setup: create an archive for this self-contained example.
    target = Path(directory) / "records.zip"
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("nested/records.txt", b"alpha\nbeta")
    # Consumer: use the same public call for every supported source.
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

The CLI accepts the same archive target and persists offsets in the uncompressed payload's byte coordinates. For `records.zip`, its default outputs are `records.sqlite3` and `records.u64` beside the archive. Signature evidence takes precedence over a conflicting suffix, and invalid suffix-claimed ZIP input cannot fall back to plain bytes.

### TAR

Plain TAR and gzip/bzip2/xz-compressed TAR follow the same sole-regular-file policy as ZIP. Accepted suffixes are `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz`, `.tbz2`, `.tar.xz` and `.txz`; supported signatures also identify unconventional filenames. Compressed data that is not TAR is rejected. Standard TAR extension headers are interpreted by the library rather than counted as payload files.

```python
import tarfile
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_stream import build_line_index

with TemporaryDirectory() as directory:
    # Fixture setup: create an archive for this self-contained example.
    target = Path(directory) / "records.tar.gz"
    payload = b"alpha\nbeta"
    with tarfile.open(target, "w:gz") as archive:
        member = tarfile.TarInfo("nested/records.txt")
        member.size = len(payload)
        archive.addfile(member, BytesIO(payload))
    # Consumer: use the same public call for every supported source.
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

TAR reads sequentially and validates entries after the selected payload before successful EOF. A later extra file or special entry invalidates the archive even after payload bytes were returned. Damaged later headers, incomplete end markers and non-padding trailing bytes fail validation. Compressed readers are drained through their available trailer/integrity checks; a corrupt footer cannot yield a completed index or CLI output pair. Early close releases resources without claiming terminal validation. For `records.tar.gz`, CLI defaults are `records.tar.sqlite3` and `records.tar.u64` beside the archive.

### 7z

7z rejects encrypted archives and unavailable codecs with `UnsupportedFormatError`. Extraction streams into a callback without creating member paths on disk. Metadata validation precedes delivery, and extraction, declared-size and available CRC checks must complete before an index or CLI outputs can be returned.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from py7zr import SevenZipFile

from archive_stream import build_line_index

with TemporaryDirectory() as directory:
    # Fixture setup: create an archive for this self-contained example.
    target = Path(directory) / "records.7z"
    with SevenZipFile(target, "w") as archive:
        archive.writestr(b"alpha\nbeta", "nested/records.txt")
    # Consumer: use the same public call for every supported source.
    assert build_line_index(target, buffer_size=2).tolist() == [0, 6, 10]
```

The [`7z adapter`](src/archive_stream/backends/sevenzip.py) forwards callback data through a [`bounded producer bridge`](src/archive_stream/backends/producer.py): one non-daemon worker, one queued block and one current consumer block, each at most 1 MiB. Callback buffers are subdivided before queueing. Dependency decompressor/callback allocations are outside those package buffer bounds.

Closing cancels package waits and joins the worker; checks during package waits occur at most 0.05 seconds apart, but dependency operations can delay cancellation, so this is not a total close-latency guarantee. Early close does not assert integrity.

For `records.7z`, CLI defaults are `records.sqlite3` and `records.u64` beside the archive.

## Scan a borrowed binary reader

`scan_line_offsets` consumes from the reader's current position, defines that position as local offset zero and neither closes nor restores the reader. It needs only a blocking `read(size) -> bytes` operation; nonempty short reads are supported.

```python
from io import BytesIO

from archive_stream import scan_line_offsets

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

## Progress logging

Indexing emits INFO records from `archive_stream.scanner`. The scanner checks at chunk boundaries and emits a periodic update once at least one second has elapsed since the previous update or scan start. It counts only complete scan buffers in the uncompressed payload, including any skipped BOM bytes. The CLI uses 1 MiB buffers. Periodic counts use binary units. The last displayed digit represents at most 100 scan buffers. With the default buffer, MiB counts are integers and GiB counts have two decimal places, as in `Scanned 2.00 GiB of uncompressed data`. A value that rounds to 1024 moves up to the next unit.

After validated EOF and offset checks, `Scan complete` gives the exact byte count, including any partial buffer. A separate line such as `Scan time: 2.35 s` gives total elapsed scan time. This covers payload reads, scanning and final validation. Opening and closing the source and writing the index files occur outside that interval. Short scans may emit only the two completion lines. Periodic updates occur at read boundaries, so a blocked read delays them.

Library use stays quiet unless the application enables INFO logging. Configure it in the application before indexing, for example:

```python
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from archive_stream import build_line_index

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
with TemporaryDirectory() as directory:
    source = Path(directory) / "events.txt"
    source.write_bytes(b"a\nb")
    assert build_line_index(source).tolist() == [0, 2, 3]
```

No root logger or console/file handler is configured by library import or scanning. Disabled progress performs no clock reads or record formatting. There are no extra payload reads, copies or extraction workers.

The CLI defaults to `--log-level INFO`. With no effective application handlers, it temporarily sends concise progress to stderr; an embedding application can instead route it through its existing handlers. `--log-level WARNING` (or ERROR/CRITICAL) suppresses progress while retaining ordinary error diagnostics. Levels are case-insensitive; DEBUG adds no per-line output. The previous scanner level is restored and only CLI-owned handlers are removed, so repeated serialized calls do not accumulate logging setup. Existing root/parent/handler settings remain application-owned. Standalone stream-only reads and row-by-row persistence do not report progress.

## Memory and failure behavior

The default scanner buffer is 1 MiB. Working payload storage is bounded by the current block and at most three BOM-probe bytes; no complete line is assembled. The offset array grows by eight bytes per line start plus the EOF sentinel, excluding object/allocation overhead. Offsets lie in `0..2^63 - 1`. Streaming alone has no indexing-range restriction.

Calling `read()` with a negative size explicitly materializes all remaining content. Use bounded reads or `readinto` for incremental consumption. Allocation, source-read and terminal-validation failures return no partial index; an unbounded read that fails late returns no partial result from that call. Owned cleanup preserves a primary exception and attaches cleanup failures; close can be retried after failed resource release.

## Line-boundary scanning

`scan_line_offsets` reads bounded byte blocks (1 MiB by default) and searches each block with repeated `bytes.find` calls. The core loop in [`scanner.py`](src/archive_stream/scanner.py), shown below as an implementation excerpt, records the byte immediately after each LF; `position` is the block’s starting offset:

```py
start = 0
while (newline := block.find(b"\n", start)) >= 0:
    append_offset(offsets, position + newline + 1)
    start = newline + 1
```

This keeps byte searching in the runtime’s native `bytes` implementation, with Python work per match rather than per byte, and never assembles a complete line. A one-byte LF needs no overlap between blocks; BOM handling and the final EOF sentinel are managed outside this loop. Python byte-by-byte iteration adds interpreter work, `readline()`/`split()` materialize lines or fragments, and `mmap` requires a suitable file rather than the generic binary-reader interface. Blockwise `bytes.find` fits the bounded-memory streaming contract without an extra scanning dependency.

## Development and artifact verification

Install the configured development/test groups using the same Python interpreter that runs the suite. These groups include the build frontend and Hatchling backend needed by integration tests that build packages without build isolation. Pytest requires `pytest-asyncio` and `pytest-timeout` and reports a clear prerequisite error if either is missing or disabled. Then run checks from the root:

```bash
python -m pip install ".[dev,test]"
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m mypy
python -m pytest --cov=archive_stream --cov-report=term-missing
python -m build
python scripts/check_release_artifacts.py --dist dist --tag v0.5.2 --write-checksums
python scripts/check_release_artifacts.py --dist dist --tag v0.5.2
python -m scripts.prepare_release --native-dist dist --output release --tag v0.5.2
python -m scripts.prepare_release --output release --tag v0.5.2 --check
```

From a checkout, build private native package inputs with `python -m build`.

Each hosted bundle has a stable version-free name. `archive-stream-wheel.zip` contains one native wheel. `archive-stream-source.zip` contains one source distribution that independently rebuilds the wheel. Version identity remains in package metadata, internal native filenames and the release tag.

Use clean `dist` and `release` directories: `dist` contains private native build inputs, while `release` is the complete hosted inventory of wheel/source ZIP bundles and SHA256SUMS. The native checker verifies package/tag/metadata agreement, safe contents, console entry points, and source/wheel package equality. The release checker independently rejects versions in every hosted filename, validates the bundled native pair and verifies outer checksums; neither command publishes a release. The actual naming gate is tested against the shared notation vectors, including historical and single-component versions with matching faulty expected names. Installed integration tests build both artifacts, independently rebuild from the source distribution, and exercise clean runtimes outside the checkout. If mypy's native parser fails during container process discovery, `python -m mypy --no-native-parser` retains strict checking with its supported Python parser.

The [public API design](docs/dev/decomposition/public-api.md) and [contracts](docs/dev/SPEC.md) define the complete intended system. [Project brief](docs/dev/PROJECT.md), [architecture](docs/dev/ARCHITECTURE.md), [delivery plan](docs/dev/PLAN.md) and [implementation tasks](docs/dev/TASKS.md) describe scope and delivery. Development uses [SDD Manager](SDD-MANAGER.md); see the [AI-assisted development disclosure](AI_DISCLOSURE.md).
