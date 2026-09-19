# Persistence specification

## 1. Scope

This specification defines conversion between the canonical `array("Q")` offset sequence and two independent path-based persistence formats:

1. a dedicated SQLite database;
2. a headerless raw little-endian unsigned 64-bit file.

It also defines validation, destination protection, safe publication, loading, and failure behavior.

The offset sequence and EOF-sentinel contract are canonical in [line-index.md](line-index.md). Public signatures and common errors are defined in [public-api.md](public-api.md).

## 2. Shared persistence rules

Both formats store exactly the values in the canonical offset array, in ascending order, including the final EOF sentinel.

Before writing, the complete array is structurally validated. A writer shall not create a temporary or destination file for an invalid array.

Persistence paths are explicit caller arguments. The package shall not:

- derive a destination from an archive name;
- store an archive path or member name;
- compute source identity or staleness metadata;
- coordinate SQLite and raw writes as one transaction;
- assume the two representations are colocated.

The two formats are independently complete. Either can reconstruct the same in-memory array without the other.

## 3. Destination protection and publication

Each writer uses the following policy:

1. Validate all non-I/O arguments and the complete offset array.
2. If the destination exists and `overwrite=False`, raise `FileExistsError` before creating a temporary file.
3. Create a uniquely named temporary sibling in the destination directory.
4. Write, flush, close, and perform the format-specific completion checks on the temporary representation.
5. When practical, flush file data through the operating system before publication.
6. If the destination appeared concurrently and `overwrite=False`, fail without replacing it.
7. Publish with an atomic same-filesystem replace/rename operation.
8. Remove the temporary file after any pre-publication failure.

With `overwrite=True`, publication atomically replaces the entire dedicated destination file. It does not update an existing database in place or preserve unrelated tables.

Atomic replacement guarantees that observers see the previous complete file or the new complete file, not a partially written file, to the extent guaranteed by the host filesystem. It does not promise multi-file atomicity or survival of every power-loss scenario.

On Windows, replacement may fail if another process has the destination open. That ordinary filesystem failure is surfaced, the previous destination remains unchanged, and the temporary file is cleaned.

## 4. SQLite format

### 4.1 Database scope

The SQLite output is a dedicated index database. Its only user-defined schema object is:

```sql
CREATE TABLE line_index (
    offset INTEGER PRIMARY KEY
);
```

No line number, length, metadata, version, source identity, or format table is stored. SQLite internal schema objects are not user-defined additions.

### 4.2 Stored rows

Every array value is inserted once, including the EOF sentinel. Because the canonical array is strictly increasing after its first value, the primary key preserves uniqueness and numeric order.

For a valid database:

```text
row count         = line count + 1
maximum offset    = indexed EOF
minimum offset    = 0 or 3
```

An empty or BOM-only payload still produces one row containing its EOF sentinel.

### 4.3 Writing

The SQLite writer creates a new temporary database, creates the canonical table, and inserts offsets within one explicit transaction. It uses parameterized insertion and bounded batches or `executemany`; SQL text is never constructed from offset values.

The transaction commits only after all values are inserted. Before publication, the writer verifies database integrity plus the expected row count and boundary values. Exact equality follows from prior array validation, parameterized insertion of every input value, primary-key uniqueness, successful statement completion, and the committed row count; a second full ordered read is not required during writing.

SQLite configuration may optimize construction of this disposable temporary database, but it must not weaken the guarantee that only a successfully closed and validated database is published.

### 4.4 Reading

The SQLite reader opens the database read-only where the platform/API permits and validates:

- the `line_index` table exists;
- its schema is exactly one `INTEGER PRIMARY KEY` column named `offset`;
- no additional user-defined table, index, view, or trigger exists;
- at least one row exists;
- every selected value is an integer in range;
- `SELECT offset FROM line_index ORDER BY offset` produces a structurally valid canonical sequence.

The reader appends values to a new `array("Q")` and returns it only after complete validation. It does not use `LIMIT ... OFFSET` for ordinal access; the entire persistence API is load/store, not database-backed random line-number lookup.

Malformed schema or values raise `InvalidIndexError`. Operational SQLite failures that do not mean malformed index content raise `PersistenceError` with the original `sqlite3` exception chained.

## 5. Raw binary format

### 5.1 Encoding

The raw file is exactly:

```text
uint64 little-endian offsets[0]
uint64 little-endian offsets[1]
...
uint64 little-endian offsets[N]  # EOF sentinel
```

There is no header, magic value, version, count, checksum, padding, alignment record, BOM, or trailing data.

The expected file size is:

```python
8 * len(offsets)
```

and is always at least eight bytes.

### 5.2 Writing

The in-memory `array("Q")` uses native byte order. On a little-endian host, the writer may write its contiguous bytes directly. On a big-endian host, it writes a byte-swapped copy or equivalent little-endian serialization without mutating the caller's array.

The writer verifies that every serialized byte was accepted and that the closed temporary file has the expected size before publication. Exact equality follows from prior array validation and deterministic serialization; a second full read-back is not required during writing.

The writer never appends to an existing raw file.

### 5.3 Reading

The raw reader validates before returning:

- file size is nonzero;
- file size is divisible by eight;
- all complete records decode as little-endian unsigned 64-bit values;
- decoded values fit `0..2^63 - 1`;
- the resulting array satisfies every structural offset invariant.

On a little-endian host, bytes may be loaded directly into `array("Q")`. On a big-endian host, the loaded array is byte-swapped after reading. Partial records, empty files, invalid first offsets, duplicate/nonmonotonic values, and out-of-range values raise `InvalidIndexError`.

The current reader loads the complete index into memory. Memory mapping and lazy binary access are outside scope, although the file format remains compatible with a later mmap reader.

## 6. Cross-format equivalence

Given one validated array:

```text
original array
    = SQLite offsets ordered ascending
    = raw uint64-le values in file order
```

Round trips through either format shall preserve every value exactly. A write followed by a read returns an array with type code `"Q"`, item size eight, and the same ordered integer sequence.

SQLite row ordering is requested explicitly with `ORDER BY offset`; physical row layout is not part of the format contract.

## 7. Failure behavior

- Invalid input arrays fail before filesystem mutation.
- Protected existing destinations raise `FileExistsError`.
- Missing read sources raise `FileNotFoundError`.
- Permission and path failures retain appropriate `OSError` subclasses.
- Malformed persisted content raises `InvalidIndexError`.
- SQLite engine or raw I/O failures without a narrower ordinary exception raise `PersistenceError` with their cause retained.
- Failed writes remove their temporary sibling when possible.
- Failed replacement leaves the previous destination intact.
- A cleanup failure may be attached as an exception note or chained context but must not hide the primary failure.

## 8. Concurrency

Writers do not provide locking between competing processes. Atomic publication prevents partial files, but two simultaneously authorized writers may race and the last successful atomic replacement wins.

With `overwrite=False`, writers perform both an initial existence check and a publication-time protection check where the platform permits. No portable cross-platform guarantee can eliminate every check/rename race without a locking protocol, which is outside scope.

Readers expect a stable complete file. Atomic writer publication supports this for readers that open either the old or new path version. Behavior when another external process modifies a file in place is outside scope.

## 9. Acceptance conditions

Persistence conforms when:

1. Empty, BOM-only, single-line, multiline, and large generated indexes round trip exactly through both formats.
2. SQLite contains the exact canonical table and one row per array value.
3. Raw bytes match explicit little-endian `uint64` encoding independent of host byte order.
4. The two loaded arrays are identical to each other and to the source array.
5. Existing destinations are not modified without `overwrite=True`.
6. Failures before publication preserve the previous destination and leave no completed-looking temporary artifact.
7. Missing tables, altered SQLite schemas, empty tables/files, partial raw records, invalid first offsets, duplicates, nonmonotonic values, and out-of-range integers are rejected.
8. Loading a raw index uses ordinary memory rather than `mmap`.
9. No source/archive identity or metadata is written in either format.
