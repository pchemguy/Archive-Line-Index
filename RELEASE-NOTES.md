Archive Line Index 0.2.0 adds independent SQLite/raw index persistence and a minimal single-target CLI to the existing plain-file streaming and indexing library.

## Highlights

- Store and reload canonical offsets through `write_sqlite_index`, `read_sqlite_index`, `write_raw_index` and `read_raw_index`, independently of any payload source. SQLite uses the dedicated `line_index(offset INTEGER PRIMARY KEY)` table; raw files are headerless little-endian unsigned 64-bit values.
- Index one target once through `archive-line-index`, `python -m archive_line_index` or the importable `archive_line_index.cli.main`. The same completed array is written to SQLite first and raw second.
- Default outputs use the input directory and filename stem with `.sqlite3` and `.u64`. Supply `--output OUTPUT_STEM` for a shared explicit stem and `--overwrite` to replace distinct existing outputs. Both paths and source aliases are checked before scanning.
- Preserve protected destinations at publication time, including concurrent creation and dangling links. Complete files are independently published; failure diagnostics identify known completed outputs and post-publication cleanup. Interruption returns status 130 and cleans owned resources.
- Retain the existing stream/LF/BOM/index behavior and expand the README with input/output/interface guidance and five executable library/CLI examples.

## Installation and use

Requires Python 3.11 or later. Download the attached wheel or source distribution and SHA256SUMS, verify their bytes, then install:

```bash
python -m pip install archive_line_index-0.2.0-py3-none-any.whl
archive-line-index data/events.txt
python -m archive_line_index data/events.txt --output results/custom
```

These examples assume the target and the `results` directory already exist. Parent directories are not created automatically. An existing output requires explicit overwrite; output aliases of the source are rejected even with overwrite. Use `--` before a hyphen-prefixed target. The source artifact `archive_line_index-0.2.0.tar.gz` independently rebuilds the wheel. Declared runtime dependencies install normally; development tools and separate archive programs are not needed for installed use.

## Publication and error behavior

There is no two-file transaction. If SQLite completes and raw fails, SQLite remains published and the diagnostic identifies it. A cleanup error after either publication also retains that complete file and its publication note. Help returns 0, usage errors 2 and expected operational errors 1; the imported callable returns these statuses without exiting its caller. Independent library APIs continue raising Python exceptions directly.

## Verification and limitations

Verification covers 399 passing tests, 96% production coverage, lint/format and strict type checks, native source/wheel builds, source rebuild and clean installed workflows outside the checkout. Console, module and imported forms produce equivalent readable pairs; real filesystem failure and SIGINT cleanup are exercised. SQLite schema validation, committed WAL visibility, pre/post-publication faults and simulated endian conversion are covered. Runtime checks ran on Linux with CPython 3.12.14; native Windows, macOS, Python 3.11 and big-endian execution remain unverified.

Payload input remains plain files or caller-supplied blocking binary readers. ZIP/TAR/7z delivery is planned for subsequent phases and recognized archive candidates are rejected explicitly. Inputs must remain stable during an operation. CLI options deliberately remain limited to one target, output stem and overwrite; library controls retain their existing defaults and signatures.
