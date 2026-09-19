# Archive streams plan

## 1. Capability delivered

This phase extends the stable plain content-stream/index pipeline to every supported archive format:

- ZIP;
- TAR and supported compressed-TAR variants;
- 7z through a bounded push-to-pull adapter.

At completion, equivalent content produces identical public byte streams and offset arrays across plain, ZIP, TAR, and 7z inputs. Archive validation, encryption rejection, terminal integrity, early close, and resource cleanup obey one public contract despite backend differences.

## 2. Specifications implemented

This phase completes:

- [../spec/archive-handling.md](../spec/archive-handling.md);
- archive-related portions of [../spec/content-stream.md](../spec/content-stream.md);
- archive-related errors and timing in [../spec/public-api.md](../spec/public-api.md);
- cross-format completion conditions in [../spec/line-index.md](../spec/line-index.md).

It does not implement SQLite or raw persistence.

## 3. Prerequisites

- The plain stream and index MVP is complete and passing.
- Backend base, content stream, scanner, source ownership, format detection, and public composition contracts are stable.
- A compatible `py7zr` release range has been selected from supported releases, declared in `pyproject.toml`, and installed in the test environment.

## 4. Ordered implementation tasks

### Task: establish shared archive test factories

Create `tests/helpers/archive_factory.py` and the initial `tests/fixtures/README.md`.

Implement test-only creation of equivalent ZIP, TAR, compressed-TAR, and 7z archives under `tmp_path`, including directories, nested member names, empty members, multiple members, and supported special entries where constructible.

Document any immutable encrypted or corrupt fixture that cannot be generated reliably. Do not commit large archives or call production code to construct expected inputs.

Run a focused helper smoke test from the first backend test that consumes it; helper modules need not have independent tests when their behavior is fully observed through backend tests.

### Task: implement ZIP archive streaming

Create `src/archive_line_index/backends/zip.py` and `tests/unit/backends/test_zip.py`.

Implement complete entry inspection, exactly-one-regular-member validation, directory exclusion, special/metadata entry rejection, encrypted-member classification, selected-member streaming, CRC/truncation error translation, and ownership-safe cleanup.

Tests cover path and seekable caller-stream input, directories plus one file, nested paths, zero/multiple files, metadata files, encrypted content, corrupt and truncated archives, declared-size rejection, early close, and caller-source non-closure.

Run ZIP tests plus source, format, stream, registry, and error tests.

### Task: register and integrate ZIP

Update `backends/registry.py` and `tests/unit/backends/test_registry.py`, then extend `tests/integration/test_content_stream.py` and `tests/integration/test_index_building.py` with plain-versus-ZIP parameterization.

Verify byte-identical bounded reads, every shared line corpus, terminal CRC failure timing, and public exception classes.

Run the affected registry and integration tests plus all ZIP dependents.

### Task: implement seekable TAR streaming

Create `src/archive_line_index/backends/tar.py` and `tests/unit/backends/test_tar.py` with initial seekable path/stream support.

Implement uncompressed and supported compressed TAR opening, complete member inspection, regular/directory/special classification, selected-member reads, error translation, and cleanup without filesystem extraction.

Tests cover `.tar`, `.tar.gz`/`.tgz`, `.tar.bz2`/`.tbz2`, and `.tar.xz`/`.txz` where supported by the runtime; nested paths; empty members; zero/multiple files; link/special/metadata entries; corruption; early close; and caller ownership.

Run TAR tests plus common source, format, stream, and error tests.

### Task: add non-seekable streaming TAR completion

Extend `backends/tar.py`, `test_tar.py`, and controlled streams in `tests/helpers/streams.py` for non-seekable TAR input.

Implement streaming member discovery, delivery of the accepted member, and continued trailing-header validation before terminal EOF. Ensure a later extra or special member raises `ArchiveStructureError` rather than returning EOF, even after earlier payload bytes were delivered.

Tests explicitly verify late structure failure timing, short source reads, early close while member/trailing data remains, and absence of extraction artifacts.

Run all TAR and content-stream lifecycle tests.

### Task: register and integrate TAR

Update the registry tests and cross-format integration parameterization for all available TAR variants.

Verify plain/ZIP/TAR equality for public reads and indexes and verify suffix- claimed but invalid compressed TAR inputs fail as archives rather than falling back to plain.

Run registry, format, content-stream, index-building, ZIP, and TAR tests.

### Task: implement the 7z queue protocol

Begin `src/archive_line_index/backends/sevenzip.py` with internal queue message types, cancellation state, and a backend reader exercised without real decompression in `tests/unit/backends/test_sevenzip.py`.

Implement distinct payload/completion/failure messages, one-slot backpressure, one-mebibyte callback subdivision, consumer read splitting/coalescing, cooperative cancellation, blocked-producer unblocking, and deterministic worker join.

Tests use a controlled producer to verify ordering, arbitrary read sizes, slow consumer backpressure, transported failures, cancellation races, idempotent close, and no live worker after close.

Run sevenzip queue tests plus common stream lifecycle tests.

### Task: implement the py7zr extraction destination

Extend `backends/sevenzip.py` and `test_sevenzip.py` with the custom `WriterFactory`/`Py7zIO` implementation required by the constrained dependency range.

Implement callback methods, selected-member routing, byte delivery into the bounded protocol, cancellation checks, and successful/failing terminal signals. No in-memory complete-member destination is permitted.

Tests exercise callback writes split below, at, and above one mebibyte; dependency-required seek/size methods; cancellation during callback delivery; and callback exceptions with retained causes.

Run all sevenzip and stream tests.

### Task: implement 7z inspection and public error translation

Complete `backends/sevenzip.py` with archive opening, full entry validation, empty-member support, encrypted-archive detection, selected-member extraction, declared-size precheck, extraction/CRC translation, ownership-safe source handling, and all cleanup paths.

Tests cover path and seekable caller sources, non-seekable rejection, zero/one/ multiple members, directories, nested paths, special or metadata entries where representable, encrypted archives, corruption/truncation, declared and actual size limits, early close, and worker failure after prefix delivery.

Run sevenzip, source, format, stream, and error tests.

### Task: register and integrate 7z

Update `backends/registry.py`, registry tests, and both cross-format integration files. The registry now supports every detected final format and no longer uses the MVP unsupported branches for ZIP, TAR, or 7z.

Verify equivalent reads/indexes across all formats, complete shared edge-case corpora, public error stability, and terminal validation timing.

Run the entire unit and integration suite.

### Task: complete resource-lifecycle integration tests

Create `tests/integration/test_resource_lifecycle.py` covering every backend.

Verify:

- normal exhaustion;
- explicit early close;
- context exit after a consumer exception;
- size-limit failure;
- corrupt/truncated input;
- caller-owned stream preservation;
- package-owned file closure;
- repeated close;
- 7z worker termination and queue unblocking;
- no temporary extracted member files.

Run the lifecycle file repeatedly to expose timing-sensitive failures, then run the full suite once more.

## 5. Phase verification

After all tasks:

1. Run every unit and integration test.
2. Run configured static and formatting checks.
3. Execute the shared corpus through plain, ZIP, every available TAR variant, and 7z.
4. Verify misleading suffix and signature-without-suffix cases.
5. Run encrypted, corrupt, truncated, multi-member, and special-entry cases.
6. Run slow-consumer 7z backpressure and repeated cleanup tests.
7. Run a large compressed-input memory test confirming no complete extracted member is retained or written to disk.
8. Build/install a wheel and repeat one workflow per archive format outside the repository.

## 6. Completion conditions

The phase is complete when:

- every supported backend conforms to the common stream contract;
- equivalent payloads produce identical public reads and offsets;
- all late failures are raised instead of appearing as successful EOF;
- no backend extracts to disk or closes caller-owned streams;
- no 7z worker survives deterministic cleanup;
- dependency direction remains acyclic and `py7zr` remains isolated to the 7z backend;
- all phase and prior-phase tests pass.
