# Index-persistence contract

## Scope and shared validation

SQLite and raw persistence independently store the completed offset model in [DECOMPOSITION](../DECOMPOSITION.md). Public functions are declared in [public API design](../decomposition/public-api.md); [internal API design](../decomposition/internal-api.md) defines the publication/temporary-path boundary. This document owns both storage formats and their publication outcomes.

Writers validate the full array and non-I/O arguments before creating a temporary file or changing a destination. Readers validate the complete stored representation before returning a new array. Both preserve the EOF sentinel and the exact ordered values. Paths are explicit; there is no automatic naming, source metadata, archive association, append operation or two-output transaction.

## Publication and cleanup

Each writer checks protected-destination existence before allocating its temporary sibling, builds and validates a complete representation in that sibling, closes all format handles and publishes only then. File data is flushed before publication; where supported, the temporary file is synchronized to the operating system. No directory/power-loss durability guarantee is implied.

With `overwrite=False`, protected creation uses a publication primitive that cannot replace an already existing destination, including a dangling symlink or a destination created after the initial check. A link-based exclusive publish is allowed; the temporary name is removed separately afterward. If exclusive publication is unavailable on the filesystem, the operation fails rather than falling back to a check followed by overwriting rename. With `overwrite=True`, an atomic same-filesystem replacement publishes the whole completed file; it does not mutate an existing database in place or preserve unrelated tables.

| Outcome | Destination guarantee and reported result |
| --- | --- |
| Invalid input or protected destination | Raise the documented validation error or `FileExistsError`; no temporary or destination mutation occurs. |
| Build, validation, flush, close or publication failure before the commit point | Raise the primary error; any previous destination remains intact, or an initially absent destination remains absent unless created by another actor. Remove the owned temporary path when possible. |
| Publication succeeds and cleanup succeeds | Return `None`; destination contains the complete valid representation. |
| Publication succeeds but removing an owned temporary name fails | Keep the complete published destination. Raise the cleanup `OSError` with a note that publication already succeeded; do not roll back or claim the previous destination survived. A temporary name may remain. |
| Cleanup also fails while another error is propagating | Preserve the original primary error and attach cleanup context; do not replace it or assert that all temporary files were removed. |

The commit point is successful exclusive creation or replacement by the underlying publication primitive. The helper performs no later cleanup within that operation, so the writer can identify whether cleanup failed before or after publication. Filesystem errors on Windows because another process holds a destination open remain ordinary errors. Competing authorized replacement writers may each publish a complete file; the last successful replacement wins. No interprocess writer locks are provided.

## SQLite representation

The dedicated database has exactly one user-defined schema object, the following rowid table; SQLite internal objects are not additional user-defined schema:

```sql
CREATE TABLE line_index (
    offset INTEGER PRIMARY KEY
);
```

One row stores each array value, including EOF. There is no line-number, length, metadata or source table. Ordering is explicitly `SELECT offset FROM line_index ORDER BY offset`; physical row layout is irrelevant. Writers create the table and insert all values using parameterized statements in a transaction. Before publication they commit, check database integrity, row count and boundary values, and close the connection. The published database is self-contained: required data cannot remain only in a WAL/journal sidecar. If WAL is used during construction, checkpoint it completely and remove owned sidecars after closing; alternatively avoid WAL. Format-owned temporary sidecars are cleaned on failure, without deleting unrelated destination files. Prior validated values, successful inserts, uniqueness and matching counts establish write completeness without requiring a second full-array load.

Readers open a stable existing database read-only and validate table/column declaration, rowid primary-key structure, absence of other user-defined objects, database integrity, nonzero row count and the canonical ordered offset sequence. Equivalent-looking schemas with extra columns, tables, indexes, views or triggers, wrong declared types or a `WITHOUT ROWID` layout are invalid. Corrupt databases and schema/value defects raise `InvalidIndexError`. Engine operational failures not indicating malformed stored content raise `PersistenceError` with their cause. Missing or inaccessible filesystem paths retain their appropriate ordinary errors.

## Raw representation

The raw file is exactly consecutive unsigned 64-bit little-endian values in array order, including EOF. It has no header, magic, version, count, checksum, padding or trailing records. Its size is exactly `8 * len(offsets)` and at least eight bytes. Native big-endian hosts convert byte order without modifying the borrowed input array.

Writers verify completion of all writes and the final temporary-file size before publication. Readers use ordinary memory, reject empty files or sizes not divisible by eight, decode every complete record in little-endian order and validate the resulting canonical array. An incomplete read of a stable file, invalid first offset, invalid singleton, duplicate/decreasing value or value exceeding `2^63 - 1` raises `InvalidIndexError`. No partial array is returned.

Raw filesystem I/O failures preserve their appropriate ordinary errors. No mmap, lazy record lookup or source verification occurs. SQLite and raw reads of equivalent indexes return arrays with identical values, type code `Q` and eight-byte items.

## Acceptance

- PER-01: Empty, BOM-only, single-line, multiline and large generated arrays round-trip through both formats with exact value/type equivalence.
- PER-02: SQLite has precisely the canonical user schema and one row per array value; raw bytes equal an explicit little-endian encoding including EOF.
- PER-03: Invalid arrays/options fail before temporary allocation; protected existing destinations, dangling symlinks and destinations created at the commit point are not replaced.
- PER-04: Authorized replacement exposes a complete file and pre-publication failures preserve the previous destination; unsupported exclusive-publication facilities fail safely.
- PER-05: Failure injection distinguishes pre-publication errors from post-publication cleanup errors, with accurate destination state and retained primary/secondary error context.
- PER-06: Wrong SQLite schemas, corrupt databases, empty/partial raw files, invalid first offsets/singletons, nonmonotonic values and out-of-range values are rejected without input mutation or partial output arrays.
- PER-07: Simulated opposite-endian conversion preserves exact raw bytes and does not mutate a supplied array; installed-package workflows can persist/reload without any payload source present.
