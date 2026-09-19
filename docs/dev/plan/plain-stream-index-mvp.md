# Plain stream and index MVP plan

## 1. Capability delivered

This phase delivers the smallest useful Archive Line Index package:

- plain path and caller-owned binary-stream sources;
- a public read-only sequential `ContentStream`;
- bounded reads, byte counting, size limits, and deterministic cleanup;
- LF byte-line indexing with optional initial UTF-8 BOM exclusion;
- the canonical `array("Q")` representation and EOF sentinel;
- public direct-scan and source-based build functions.

Archive signatures are recognized so compressed input is not silently treated as plain, but ZIP, TAR, and 7z opening remains unavailable until the next phase. Persistence remains unavailable until the persistence phase.

## 2. Specifications implemented

This phase implements:

- [../spec/public-api.md](../spec/public-api.md): runtime, source type, constants, content-stream API, scanning/build API, validation, ownership, and foundational exceptions;
- [../spec/content-stream.md](../spec/content-stream.md): behavior applicable to pull-based plain sources;
- [../spec/archive-handling.md](../spec/archive-handling.md): detection rules and plain backend only;
- [../spec/line-index.md](../spec/line-index.md): complete in-memory indexing contract.

It does not implement archive decompression or either persistence format.

## 3. Prerequisites

- Python 3.11 or later.
- A working virtual environment or equivalent isolated test environment.
- Packaging and test tools permitted by the repository configuration.
- No runtime archive dependency is required for the first plain-only tasks; `py7zr` metadata may be declared once its tested range is verified.

## 4. Ordered implementation tasks

### Task: establish the package and test baseline

Create `pyproject.toml`, the `src/archive_line_index/` package directory, minimal `__init__.py`, test directories, `.gitignore`, and the initial pytest configuration.

Requirements:

- use `src` package discovery;
- require Python 3.11+;
- ensure tests import the installed/editable package rather than modifying `sys.path`;
- configure deterministic test discovery under `tests/`;
- keep `__init__.py` empty of provisional exports until the public composition exists.

Verification:

- create and activate an isolated environment using an available permitted mechanism;
- install the project editable with test dependencies;
- run a smoke test importing `archive_line_index`;
- run `python -m pytest` and confirm the empty/baseline suite executes normally.

### Task: implement public errors

Create `src/archive_line_index/errors.py` with the complete exception hierarchy specified for the final project. Add `tests/unit/test_errors.py`.

Tests verify inheritance, stable names, and that ordinary filesystem and argument errors are not redefined as package exceptions.

After the focused tests, run the package import smoke test.

### Task: implement source ownership and prefix replay

Create `src/archive_line_index/sources.py` and `tests/unit/test_sources.py`.

Implement path opening, caller-stream attachment, ownership tracking, seekability reporting, binary-read validation, bounded prefix reading/replay, and idempotent release of owned handles.

Tests cover:

- string and path-like sources;
- missing and inaccessible paths;
- seekable and non-seekable streams;
- current-position preservation as the processing origin;
- replay with prefixes split by short reads;
- rejection of text streams;
- package-owned closure and caller-owned non-closure;
- repeated cleanup.

Run `test_sources.py` and `test_errors.py`.

### Task: implement format classification

Create `src/archive_line_index/formats.py` and `tests/unit/test_formats.py`.

Implement the internal format identifier, bounded signature probing, recognized compound suffixes, content-first precedence, strict suffix claims, and plain fallback. At this phase, detection identifies all final candidates even though the archive registry cannot yet open them.

Tests cover every supported signature/suffix combination, unconventional archive names, misleading recognized suffixes, unknown/plain suffixes, case-insensitive matching, and prefix replay requirements.

Run format, source, and error unit tests.

### Task: define the backend reader contract

Create `src/archive_line_index/backends/base.py`. Add focused protocol/fake-reader coverage to `tests/unit/test_stream.py` rather than creating a second abstract test hierarchy.

Define the minimal internal read/close/completion interface needed by the common stream. Do not include line scanning, format detection, persistence, or public construction concerns.

Run the focused stream contract tests and import checks.

### Task: implement the plain backend

Create `src/archive_line_index/backends/plain.py` and `tests/unit/backends/test_plain.py`.

Adapt source handles to bounded reads, preserve replay prefixes, and implement owned/caller-owned cleanup through the backend contract.

Tests cover empty and large sources, arbitrary short reads, replay boundaries, read failures, early close, and ownership.

Run plain-backend tests plus source and stream-contract tests.

### Task: implement backend dispatch for the MVP

Create `src/archive_line_index/backends/registry.py` and `tests/unit/backends/test_registry.py`. Keep `backends/__init__.py` free of eager concrete imports.

Register the plain backend. For detected ZIP, TAR, or 7z candidates, dispatch shall raise `UnsupportedFormatError` during this phase rather than treating compressed bytes as plain. The next phase replaces those unsupported branches with concrete factories without changing the registry contract.

Run registry, format, and plain-backend tests.

### Task: implement the common content stream

Create `src/archive_line_index/stream.py` and complete `tests/unit/test_stream.py`.

Implement readable binary behavior, arbitrary bounded read sizes, `readinto`, internal buffering, actual-byte size enforcement, successful EOF state, idempotent close, context management, and delegation to fake/plain readers.

Tests cover zero, bounded, short, and unbounded reads; exact and exceeded size limits; error-before-EOF behavior; repeat EOF; unsupported operations; closure after consumer exceptions; and no closure of caller-owned sources.

Run stream, backend base/plain, source, and error tests.

### Task: implement the offset representation

Create `src/archive_line_index/offsets.py` and `tests/unit/test_offsets.py`.

Implement `array("Q")` construction, item-size verification, structural validation, shared signed-range enforcement, line-count/range derivation, and the mandatory EOF-sentinel rules.

Tests cover every valid zero-/one-/multi-line shape and wrong type code, empty array, invalid first offset, duplicate, descending, oversized, and non-array inputs.

Run offset and error tests.

### Task: implement the byte-line scanner

Create `src/archive_line_index/scanner.py` and `tests/unit/test_scanner.py` using the shared cases from `tests/helpers/binary_cases.py` and controlled streams from `tests/helpers/streams.py`.

Implement split BOM probing, prefix replay, block reads, repeated `bytes.find(b"\n")`, absolute positions, final unterminated-line handling, EOF sentinel insertion, and final structural validation.

Tests cover the complete line-index example table, every relevant block split, short-read patterns, a line larger than the buffer, read failures, source non-closure, invalid buffer sizes, and a guard against a Python per-byte scan implementation.

Run scanner, offset, and error tests.

### Task: compose the MVP public API

Create `src/archive_line_index/api.py` and integration tests in `tests/integration/test_content_stream.py` and `tests/integration/test_index_building.py` for plain sources.

Implement `open_content_stream()`, `scan_line_offsets()`, and `build_line_index()` as thin composition. Add the initial final public exports for these capabilities to `__init__.py`; persistence names may be added only when implemented.

Tests cover path and caller-stream workflows, source position, deterministic cleanup, package/caller ownership, BOM policy, max size, direct-versus-composed index equality, and archive-candidate rejection during the MVP.

Run all unit tests plus both integration files.

## 5. Phase verification

After all tasks:

1. Run the complete implemented pytest suite.
2. Run configured formatting and static-analysis checks.
3. Build a wheel and install it into a clean environment.
4. From outside the repository, import the current public names.
5. Stream and index plain files containing the complete shared byte corpus.
6. Confirm caller-owned streams remain open after success and failure.
7. Confirm archive signatures are rejected rather than indexed as plain bytes.
8. Run a generated large plain-input test demonstrating memory proportional to offsets and bounded buffers, not payload size or longest line.

## 6. Completion conditions

The phase is complete when:

- every task and phase verification passes;
- the public API can stream and index plain input correctly;
- the canonical offset structure is stable for dependent archive and persistence phases;
- no implementation depends on archive-specific behavior;
- no temporary archive, persistence, CLI, metadata, or mmap functionality has been added;
- documentation matches any implementation-level decisions discovered during the phase.
