# Archive-handling specification

## 1. Scope

This specification defines source-format detection, supported unencrypted archive formats, archive structure, backend selection, backend-specific streaming behavior, and error classification.

The common public byte-stream contract is defined in [content-stream.md](content-stream.md). Source ownership and public exceptions are defined in [public-api.md](public-api.md).

## 2. Supported formats

The system supports:

- an uncompressed plain file;
- ZIP through Python's `zipfile`;
- TAR and compression filters supported by the Python 3.11+ standard-library `tarfile` build;
- 7z through `py7zr`.

Recognized TAR filename forms include at least:

```text
.tar
.tar.gz
.tgz
.tar.bz2
.tbz2
.tar.xz
.txz
```

Standalone gzip, bzip2, or xz streams that do not contain a TAR archive are not supported as compressed plain files. Password-protected or otherwise encrypted archives are outside the supported input domain for every format. The API has no password or credential input and does not define detection, classification, or extraction behavior for them.

No external `7z`, `7zz`, `tar`, or other archive executable is used.

## 3. Detection policy

Detection prefers content signatures over filename suffixes while using suffix claims to prevent silent fallback from a malformed archive to plain content.

The detector shall distinguish:

- the 7z signature;
- ZIP signatures accepted by `zipfile`;
- uncompressed TAR headers;
- gzip, bzip2, and xz signatures that may wrap TAR;
- plain content.

Rules:

1. A recognized archive signature selects that archive candidate regardless of filename.
2. A recognized TAR-compression signature selects a TAR candidate; failure to open it as TAR is an archive failure, not plain fallback.
3. A recognized archive suffix selects its corresponding candidate even when a signature is missing; invalid content raises `InvalidArchiveError`.
4. Content without a recognized archive signature or suffix is plain.
5. Plain-file suffixes are unrestricted, including `.txt`, `.jsonl`, unknown suffixes, and no suffix.
6. Suffix comparison is case-insensitive.

Detection opens the path, reads only a bounded prefix, and closes its handle. The selected backend independently opens the same path from its beginning, so detection state is never shared with payload delivery.

Content signatures identify candidate formats; the selected archive library remains authoritative for full structural validity.

## 4. Source requirements

Archive-opening operations accept filesystem paths only. The package does not inspect source positioning capabilities or select a backend strategy from seekability. Plain and TAR backends read package-owned files sequentially. `zipfile` and `py7zr` may position their own internally opened archive handles as required, while the public payload remains sequential and is never extracted.

TAR always uses sequential streaming mode. Some invalid structure may therefore be detected only after member bytes have already been delivered.

## 5. Archive structure

An accepted archive shall contain exactly one regular-file member after directory entries are excluded.

- An empty regular file counts as the one member.
- A member nested under one or more archive directories is valid.
- Member name and suffix are unrestricted.
- Directory entries do not count.
- Symbolic links, hard links, devices, FIFOs, sockets, and other special entries are invalid.
- Metadata files, including entries beneath `__MACOSX`, are not ignored.
- Zero regular files is invalid.
- More than one regular file is invalid.

Any unsupported special entry causes `ArchiveStructureError` even if exactly one regular file also exists. When practical and safe, the exception message identifies eligible or offending member names without interpreting paths on the host filesystem.

Archive member paths are untrusted metadata. They are never joined to an output directory and never passed to filesystem extraction functions.

## 6. Validation timing

For ZIP and 7z, central/member metadata normally permits archive-structure validation before payload delivery. The backend shall validate first whenever the library exposes the complete entry list without extraction.

For streaming TAR, the backend may encounter the accepted regular member before later entries. It may deliver that member sequentially, but terminal EOF must not be reported until remaining headers have been inspected and the exactly-one-member/special-entry policy has been established. A late violation raises `ArchiveStructureError` after any already returned prefix bytes.

Declared member size is advisory for resource-limit prechecks but never replaces actual decompressed-byte counting.

## 7. Plain backend

The plain backend adapts the source directly to the internal backend reader protocol.

It shall:

- read bounded byte chunks;
- preserve all bytes exactly;
- participate in actual-size counting through the common stream wrapper;
- close its package-owned source.

Plain input has no archive-structure or CRC validation beyond successful source reads through EOF.

## 8. ZIP backend

The ZIP backend shall:

- use `zipfile.ZipFile` for inspection;
- validate the complete entry set before opening the selected member;
- open only the validated regular member;
- use bounded reads from the member stream;
- close the member and archive wrappers deterministically;
- close its package-owned archive handle;
- allow `zipfile` CRC or truncation failures to surface through the package error model.

It shall not call `extract()`, `extractall()`, or create an output path.

## 9. TAR backend

The TAR backend shall:

- use `tarfile` sequential streaming mode for every path;
- support compression filters available in the supported standard-library build without implying optional undeclared filters;
- classify every encountered member;
- open and read only the validated regular member;
- continue trailing-header validation before terminal EOF where streaming mode requires it;
- close extracted-file, TAR, and owned-source objects deterministically.

It shall not call filesystem extraction methods.

## 10. 7z backend

The 7z backend shall use `py7zr.SevenZipFile` plus a custom `WriterFactory`/`Py7zIO` destination. An in-memory destination retaining the complete member is prohibited.

Because `py7zr` pushes decompressed bytes to `Py7zIO.write()`, the backend adapts push extraction to pull reads with:

```text
one non-daemon extraction worker
        → one-slot bounded block queue
        → consumer-side backend reader
```

The queue capacity is one completed payload block. Callback input larger than one mebibyte is subdivided before queueing so queue lookahead remains bounded by one block of at most one mebibyte, excluding the dependency-owned callback argument currently being processed.

The callback implementation shall:

- implement every method required by the constrained `py7zr` range;
- retain only state necessary for sequential delivery;
- check cancellation before and during block delivery;
- be safe under documented `py7zr` threading behavior;
- distinguish successful completion from failure;
- avoid silently dropping bytes during cancellation races.

The consumer reader may combine or split queued blocks to satisfy arbitrary public read sizes. Producer exceptions are chained into the public error raised by the consuming thread.

The backend validates entries before extraction whenever `py7zr` exposes a complete member list. It extracts only the accepted member into the custom destination and never to disk.

## 11. Backend error classification

Backend-specific exceptions are classified as follows:

- recognized format that cannot be parsed: `InvalidArchiveError`;
- invalid member count or entry type: `ArchiveStructureError`;
- configured declared or actual size exceeded: `SizeLimitExceededError`;
- CRC, truncated compressed data, decompressor failure, callback delivery failure, or terminal footer failure: `ExtractionError` unless a narrower classification applies;
- unsupported detected compression/archive kind: `UnsupportedFormatError`.

Original exceptions remain available as chained causes. Filesystem exceptions arising before archive interpretation retain their ordinary types.

## 12. Acceptance matrix

Equivalent byte corpora shall be exercised through every format that can represent the case. Required archive cases include:

- empty member;
- one regular member with and without directory entries;
- nested member path;
- zero and multiple regular members;
- one regular member plus a symbolic link or other special entry;
- metadata file plus the intended file;
- corrupt and truncated archives;
- misleading recognized suffixes;
- signature-recognized archives with unconventional names;
- string and path-like filesystem sources;
- declared-size and actual-size limit failures;
- early close during active extraction;
- terminal integrity failure after earlier payload delivery.

The backend set conforms when all accepted cases return identical payload bytes and all rejected cases produce the specified stable public error class without filesystem extraction or leaked resources.
