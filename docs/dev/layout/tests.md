# Test organization

## 1. Scope and test-tree rules

This node owns test locations, infrastructure, fixtures, and production-to-test mapping.

The test tree mirrors production ownership without becoming a Python package. No `tests/__init__.py` is required. Tests import the installed `archive_line_index` package or named implementation modules, never by altering `sys.path` inside test files.

## 2. Shared test infrastructure

### `tests/conftest.py`

Defines narrowly reusable pytest fixtures, temporary paths, parameter sets, and shared cleanup assertions. It must not become a miscellaneous test-helper module containing archive construction or expected-result algorithms.

### `tests/helpers/archive_factory.py`

Creates small plain, ZIP, TAR, compressed-TAR, and 7z inputs for tests. Generated archives live under pytest-provided temporary directories. Helper behavior is test infrastructure and must not import or call production archive-building logic.

### `tests/helpers/binary_cases.py`

Defines the shared byte corpora and expected offset sequences used across plain and archived representations. Canonical cases include empty content, BOM-only content, empty lines, terminal and unterminated lines, CRLF, lone CR, BOM-like bytes away from the beginning, and boundaries split across every relevant read position.

### `tests/helpers/streams.py`

Provides controlled caller-owned streams, non-seekable streams, short-read streams, failing streams, and instrumentation used to verify ownership, backpressure, closure, and error propagation.

### `tests/fixtures/`

Contains only small immutable files that are impractical or unreliable to generate during a test, such as carefully corrupted or externally produced archive cases. `README.md` records each fixture's purpose and reproducible origin. Large real-world archives and generated index outputs are never committed here.

## 3. Unit tests

Unit tests correspond directly to production ownership:

| Production owner        | Primary unit tests                |
| ----------------------- | --------------------------------- |
| `errors.py`             | `unit/test_errors.py`             |
| `sources.py`            | `unit/test_sources.py`            |
| `formats.py`            | `unit/test_formats.py`            |
| `stream.py`             | `unit/test_stream.py`             |
| `offsets.py`            | `unit/test_offsets.py`            |
| `scanner.py`            | `unit/test_scanner.py`            |
| `backends/registry.py`  | `unit/backends/test_registry.py`  |
| `backends/plain.py`     | `unit/backends/test_plain.py`     |
| `backends/zip.py`       | `unit/backends/test_zip.py`       |
| `backends/tar.py`       | `unit/backends/test_tar.py`       |
| `backends/sevenzip.py`  | `unit/backends/test_sevenzip.py`  |
| `persistence/sqlite.py` | `unit/persistence/test_sqlite.py` |
| `persistence/raw.py`    | `unit/persistence/test_raw.py`    |

`api.py` is intentionally thin; its meaningful behavior is verified primarily through integration tests. A focused unit test file may be added if it acquires nontrivial argument-validation or cleanup branches, but API composition should not be mocked into a duplicate implementation.

## 4. Integration tests

`tests/integration/test_content_stream.py` exercises public stream behavior across every supported source format, including source ownership, bounded reads, error timing, early closure, and terminal integrity.

`tests/integration/test_index_building.py` verifies that equivalent plain, ZIP, TAR, and 7z content produces the same offset sequence through the public composition path.

`tests/integration/test_persistence_equivalence.py` verifies that the completed in-memory array, rows selected from SQLite in ascending order, and decoded raw `uint64` values are identical, including the EOF sentinel.

`tests/integration/test_resource_lifecycle.py` verifies deterministic cleanup, no surviving 7z extraction worker after closure, caller-owned stream preservation, and cleanup following consumer, backend, scanner, and persistence failures.
