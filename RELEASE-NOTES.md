Archive Stream 0.5.3 makes indexing progress easier to read and adds total scan time.

## Highlights

- Periodic INFO updates use a one-second minimum interval and count the uncompressed bytes in complete scan buffers. They use binary units with precision based on the configured buffer size.
- Successful scans report the exact uncompressed byte count and total elapsed scan time through EOF and index validation. Source acquisition, cleanup and index-file writes fall outside that interval.
- The README shows the new CLI output, and artifact validation rejects malformed wheel console declarations before generating checksums.

## Usage

The indexing command remains `archive-line-index SOURCE`. Use `--log-level WARNING` for quiet progress output. Python applications can configure `archive_stream.scanner` through standard logging. Stream, index and persistence APIs retain their existing signatures and formats.

## Installation

Requires Python 3.11 or later and `py7zr>=1.1.4,<1.2`. Download `archive-stream-wheel.zip` and `SHA256SUMS`, compare the bundle's SHA-256 with the manifest, then extract and install the wheel:

```bash
python -m zipfile -e archive-stream-wheel.zip .
python -m pip install archive_stream-0.5.3-py3-none-any.whl
```

The source bundle `archive-stream-source.zip` contains `archive_stream-0.5.3.tar.gz`. Verification covers the wheel and the source-rebuilt wheel on Linux with CPython 3.12.14 and py7zr 1.1.4. Native Windows CMD and macOS execution were unavailable.
