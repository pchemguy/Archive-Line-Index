Archive Line Index 0.1.0 delivers a standalone Python library for sequential plain-file reading and exact byte-line indexing.

## Highlights

- Stream original payload bytes through `open_content_stream`, using bounded reads, `readinto` or context-managed access independently of indexing.
- Scan a caller-owned blocking binary reader with `scan_line_offsets`, or open, index and close a filesystem source with `build_line_index`.
- Obtain compact unsigned eight-byte offset arrays containing line starts and an EOF sentinel. LF/CRLF, initial UTF-8 BOM handling, empty content and unterminated final lines retain their byte-coordinate semantics.
- Apply inclusive payload-size limits, validation before source acquisition, retained read failures and deterministic owned-resource cleanup. Scanning uses bounded blocks without assembling complete lines.

## Installation and artifacts

Requires Python 3.11 or later. Download the wheel or source distribution attached to this release, together with `SHA256SUMS`. Verify the downloaded bytes against the checksum file, then install the wheel:

```bash
python -m pip install archive_line_index-0.1.0-py3-none-any.whl
```

The explicit source artifact is `archive_line_index-0.1.0.tar.gz`; it can independently rebuild the wheel. Installation resolves the declared py7zr runtime dependency; no development tools or separate archive program are needed for library use. The README provides stream-only, direct-reader and source-based examples, input/output descriptions and the Python interface overview.

## Verification and scope

Verification covers 253 passing tests, 99% production coverage, lint/format and strict type checks, native source/wheel builds, a source-distribution rebuild, both installed-library paths outside the checkout, executable README examples and artifact inventory/checksum validation. Runtime checks ran on Linux with CPython 3.12.14; native Windows, macOS and Python 3.11 execution have not been verified.

This version supports plain files and caller-supplied blocking binary readers. ZIP/TAR/7z delivery, index persistence and the single-target CLI are planned capabilities. Recognized archive candidates are rejected explicitly. Inputs must remain stable during an operation; a caller serializes access to each stream. Calling an unbounded read intentionally materializes the remaining payload, while the index array grows with line count.
