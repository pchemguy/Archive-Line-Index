# Index persistence plan

## 1. Capability delivered

This phase adds independent, validated round trips between the canonical in-memory offset array and:

- a dedicated SQLite `line_index` database;
- a headerless raw little-endian `uint64` file.

Both writers protect existing destinations by default and publish only complete validated files. Both readers reconstruct a validated `array("Q")`. The phase does not associate either file with an archive or coordinate both outputs as a single transaction.

## 2. Specifications implemented

This phase implements:

- [../spec/persistence.md](../spec/persistence.md);
- persistence functions and related errors in [../spec/public-api.md](../spec/public-api.md);
- persisted-form invariants referenced from [../spec/line-index.md](../spec/line-index.md).

## 3. Prerequisites

- Plain and archive stream/index phases are complete.
- The canonical offset validation API is stable.
- Every supported source format already produces identical offset arrays.

## 4. Ordered implementation tasks

### Milestone: persistence adapters

#### Task: finalize persistence-facing offset validation

Review `src/archive_line_index/offsets.py` and extend it only where persistence requires shared validation not already implemented. Extend `tests/unit/test_offsets.py`.

Confirm:

- concrete `array("Q")` and item-size checks;
- nonempty sequence;
- first offset `0` or `3`;
- strict monotonicity after the first value;
- shared `2^63 - 1` bound;
- zero-line `[0]` and `[3]` handling;
- validation without source identity assumptions.

Run offset, scanner, and existing integration tests to ensure the stricter checks accept every scanner-produced result.

#### Task: implement SQLite writing

Create `src/archive_line_index/persistence/sqlite.py` and `tests/unit/persistence/test_sqlite.py` with the write path first.

Implement input validation, existing-destination protection, temporary sibling creation, exact schema creation, transaction-scoped bulk insertion, rollback, integrity plus row-count/boundary validation, close/flush, atomic publication, and failure cleanup.

Tests cover `[0]`, `[3]`, normal and large arrays; exact schema/rows; destination absence/presence; `overwrite=False` and `True`; insertion/commit/validation/ replace failures; preservation of an existing destination; cleanup; unwritable directories; and signed-range boundaries.

Run SQLite-write and offset tests.

#### Task: implement SQLite reading

Extend `persistence/sqlite.py` and `test_sqlite.py` with read-only loading and strict schema/content validation.

Tests cover valid round trips, missing files, missing/renamed/extra columns, wrong primary-key/type declarations, extra user schema objects, empty tables, noninteger values where constructible, and operational database corruption.

Verify malformed index content produces `InvalidIndexError`, operational failures produce `PersistenceError` with causes, and every opened connection is closed.

Run SQLite, offsets, and error tests.

#### Task: implement raw writing

Create `src/archive_line_index/persistence/raw.py` and `tests/unit/persistence/test_raw.py` with the write path first.

Implement validation, explicit little-endian conversion, preservation of the caller's array, temporary sibling creation, complete write/flush/size and byte-count verification, destination protection, atomic publication, and cleanup.

Tests compare exact bytes against `struct.pack("<Q", value)` for every value, cover empty/BOM-only/normal/large arrays, simulate big-endian conversion logic, exercise partial/failing writes, and verify overwrite behavior and old-file preservation.

Run raw-write, offsets, and error tests.

#### Task: implement raw reading

Extend `persistence/raw.py` and `test_raw.py` with complete loading into `array("Q")`, host-endian conversion, and structural validation.

Tests cover exact round trips, missing and empty files, sizes not divisible by eight, invalid first offsets, duplicates, descending values, values over the SQLite range, simulated endian conversion, and read failures.

Assert that no `mmap` API is used or exposed.

Run raw, offsets, and scanner tests.

### Milestone: public persistence integration

#### Task: expose persistence through the public API

Add thin persistence functions to `src/archive_line_index/api.py` and their final exports to `__init__.py`. Do not add a combined two-destination write.

Extend public API integration coverage to verify validation occurs before temporary creation, explicit destinations are required, filesystem exceptions remain ordinary, and translated failures retain causes.

Run API, SQLite, raw, and error tests plus existing content/index integration tests.

#### Task: verify cross-format persistence equivalence

Create `tests/integration/test_persistence_equivalence.py`.

For every shared byte corpus and representative plain/ZIP/TAR/7z source:

1. build the in-memory index;
2. persist independently to SQLite and raw files;
3. load both representations;
4. assert identical type code, item size, values, line count, and EOF sentinel;
5. inspect SQLite ordered rows and raw bytes directly.

Include repeated replacement, failure-before-publication, and no-metadata assertions.

Run this integration file and all dependent unit tests.

## 5. Phase verification

After all tasks:

1. Run the complete test suite and configured checks.
2. Round-trip small and large generated indexes through both formats.
3. Verify exact raw little-endian bytes independently of the package reader.
4. Inspect SQLite schema independently and confirm no metadata or auxiliary user object exists.
5. Inject failures at every pre-publication boundary and verify prior destinations remain byte-identical.
6. Check that temporary siblings, journals, and WAL files are cleaned.
7. Build/install a wheel and perform both persistence round trips outside the repository.

## 6. Completion conditions

The phase is complete when:

- both formats exactly round-trip every valid canonical array;
- every malformed persisted representation is rejected;
- existing destinations are protected by default;
- authorized replacement is whole-file and failure-safe;
- SQLite and raw output remain independent and metadata-free;
- no mmap or archive-association behavior has been introduced;
- all previous stream/index tests continue to pass.
