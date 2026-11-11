# Archive Stream API reference

Optional arguments are shown at their defaults where applicable. The streaming example supplies a positive block size.

## Python library

Import these operations from `archive_stream`. A source path may be a string or a path-like object that returns a string. Archive format and decompression are selected automatically.

### Stream a payload

```python
from archive_stream import open_content_stream

with open_content_stream(source="data/events.zip", max_uncompressed_size=None) as stream:
    block = stream.read(1_048_576)
```

For bounded reads into reusable storage, allocate `buffer = bytearray(65536)` once and call `stream.readinto(buffer)` on an open stream.

| Parameter | Meaning |
| --- | --- |
| `source` | Required path to a plain file or a supported archive. |
| `max_uncompressed_size=None` | Inclusive limit in payload bytes. `None` applies no size limit. |
| `size` in `read(1_048_576)` | Positional-only byte limit. This example reads up to 1 MiB. Repeat the read to stream more blocks. An empty result with a positive size signals validated EOF. |
| `buffer` in `readinto(buffer)` | Required positional-only writable contiguous buffer. Returns the number of bytes copied and leaves the unused suffix unchanged. |

The context manager closes the stream. For manual ownership, call `stream.close()`. Use `stream.closed`, `stream.readable()`, `stream.writable()`, and `stream.seekable()` to inspect its state and capabilities. [Content stream contract](dev/spec/content-stream.md)

### Build an index

```python
from archive_stream import build_line_index, scan_line_offsets

offsets = build_line_index(
    source="data/events.zip",
    skip_utf8_bom=True,
    buffer_size=1_048_576,
    max_uncompressed_size=None,
)

with open("data/events.txt", "rb") as stream:
    borrowed_offsets = scan_line_offsets(
        stream=stream,
        skip_utf8_bom=True,
        buffer_size=1_048_576,
    )
```

| Parameter | Meaning |
| --- | --- |
| `source` | Required input path. `build_line_index` opens and closes its own stream. |
| `stream` | Required caller-owned binary reader with blocking `read(size)`. Scanning starts at its current position and leaves closure to the caller. |
| `skip_utf8_bom=True` | Exclude one leading UTF-8 BOM from first-line content while retaining original byte coordinates. |
| `buffer_size=1_048_576` | Maximum bytes requested per read. The default is 1 MiB. |
| `max_uncompressed_size=None` | Inclusive payload limit for `build_line_index`. `None` applies no size limit. |

Both functions return an `array("Q")` of line starts followed by the EOF offset. [Line-index contract](dev/spec/line-index.md)

### Store or load an index

```python
from archive_stream import (
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)

write_sqlite_index(offsets=offsets, destination="data/events.sqlite3", overwrite=False)
write_raw_index(offsets=offsets, destination="data/events.u64", overwrite=False)
sqlite_offsets = read_sqlite_index(source="data/events.sqlite3")
raw_offsets = read_raw_index(source="data/events.u64")
```

| Parameter | Meaning |
| --- | --- |
| `offsets` | Required completed offset array, including the EOF offset. |
| `destination` | Required path for the SQLite database or raw little-endian uint64 file. |
| `overwrite=False` | Protect existing destinations. Set `True` to replace an existing output. |
| `source` | Required path to an existing index file in the reader's format. |

[Persistence contract](dev/spec/persistence.md)

## CLI

Run one of these equivalent forms. The explicit output stem is the default derived from the sample target. Omit switch flags to use their false defaults.

```bash
archive-line-index data/events.zip --output data/events --log-level INFO
python -m archive_stream data/events.zip --output data/events --log-level INFO
```

```python
from archive_stream.cli import main

# Read arguments from sys.argv[1:].
status = main(argv=None)

# Or pass equivalent arguments directly.
status = main(argv=["data/events.zip", "--output", "data/events", "--log-level", "INFO"])
```

| Parameter | Default | Meaning |
| --- | --- | --- |
| `TARGET` | Required | Path to one plain file or supported archive. |
| `-o` / `--output OUTPUT_STEM` | Target directory and filename stem | Shared output path stem. The CLI appends `.sqlite3` and `.u64`. Default naming removes only the final suffix. |
| `--overwrite` | False | Supply the flag to replace existing outputs. Outputs must be distinct from the source. |
| `--log-level LEVEL` | `INFO` | Case-insensitive choice of `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. `WARNING` suppresses scan progress. |
| `-h` / `--help` | False | Supply the flag to show help and exit successfully. |
| `argv` in `main(argv=None)` | `None` | Use process arguments by default. Pass a sequence of argument strings for in-process use. Returns the CLI status as an integer. |

Both index files are written from one scan. Use `--` before a target whose name starts with a hyphen. [CLI contract](dev/spec/cli.md) · [Progress logging contract](dev/spec/progress-logging.md)
