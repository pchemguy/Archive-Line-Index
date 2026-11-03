# Archive Line Index

## Purpose and users

Archive Line Index is a synchronous Python library with a minimal importable command-line interface for developers who need to consume a large byte-oriented payload from a plain file or archive and locate its LF-delimited line ranges. Typical inputs include logs, text datasets and JSONL files; the library treats their content as bytes rather than parsing records.

It provides two independently useful capabilities: sequential payload streaming and byte-line indexing. Callers can use the stream without building an index, or scan a caller-owned binary stream without using archive handling.

## Intended outcomes

- Consume original payload bytes without extracting archive members to disk or retaining the complete decompressed payload during bounded reads.
- Build exact byte offsets while keeping scan memory independent of total payload size and the longest line. The completed index itself occupies memory proportional to line count.
- Preserve one canonical offset sequence across in-memory, SQLite and raw-binary representations.
- Provide predictable validation, errors, ownership and cleanup, including early cancellation and failures discovered after some payload bytes were delivered.
- Deliver an installable Python package with documented public APIs and evidence for functional correctness, resource lifecycle and installed-package use.

## Principal scope

### Content access

Sources are filesystem paths to plain files or unencrypted ZIP, TAR, compressed-TAR and 7z archives. An accepted archive has exactly one regular-file member; directories do not count, while additional files and special entries are rejected. Member names do not restrict payload content.

Detection prioritizes content, with recognized archive suffixes preventing silent plain-file fallback for invalid claimed archives. The public payload stream is read-only, sequential, non-seekable and context-managed. It returns unchanged bytes and supports a caller-selected maximum decompressed size.

Package-owned resources close deterministically. Successful terminal EOF includes all integrity and trailing-structure validation available from the backend; early closure releases resources without certifying unread archive content.

### Byte-line indexing

Only byte LF terminates a line. The terminator belongs to its line; CRLF is preserved, a lone CR is ordinary content, and a final unterminated byte sequence is a line. A trailing LF creates no extra line; empty input has no lines.

An initial UTF-8 BOM can be excluded from the first line without renumbering the original decompressed byte space. Indexes contain unsigned 64-bit line starts in an `array("Q")`, followed by one EOF sentinel, so adjacent values delimit each line. The shared offset range must also fit SQLite's signed integer storage.

Index construction succeeds only after complete successful consumption. A direct scanner consumes a caller-owned binary stream from its current position and does not close it.

### Persistence

Callers explicitly name index files and associate them with sources. The library independently reads and writes a dedicated SQLite database and a headerless little-endian unsigned 64-bit file. Both preserve the complete offset sequence, including the EOF sentinel, and validate loaded data.

Existing destinations are protected by default. Explicit replacement publishes a completed output and preserves the prior destination on pre-publication failure. Filesystem guarantees and concurrent-writer behavior require precise downstream contracts; there is no transaction spanning both output formats.

### Single-target command line

A user can index one filesystem target with a single positional command-line argument. The CLI builds the index through the library and writes both SQLite and raw-binary indexes in the input directory using the input filename without its final extension as the default artifact stem, with an optional explicit output stem and explicit overwrite permission. Its callable entry point is importable for in-process use; importing it performs no indexing or argument parsing.

## Constraints and quality priorities

- Python 3.11 or later, with Windows, Linux and macOS as intended platforms.
- A library API suitable for synchronous callers; internal concurrency remains a design choice rather than a public asynchronous interface.
- `py7zr` is the declared third-party runtime dependency. Standard-library ZIP, TAR and SQLite support are available; no external archive executable is required.
- Hatchling packaging and the existing pytest, Ruff, strict mypy, coverage and Flowmark configuration provide the development-tooling baseline.
- Byte fidelity, bounded payload buffering, deterministic cleanup and truthful completion guarantees take priority over speculative abstractions or unsupported performance claims. Dependency-internal resource costs must be distinguished from package-controlled buffers.

## Non-goals

- Text decoding, encoding detection, newline normalization or record validation.
- Encrypted archives, passwords, prompting or credential discovery.
- Extracted member files, multi-payload archive selection or remote sources.
- Random seeking in compressed payloads or decompression checkpoints.
- Memory-mapped or lazy index access; persisted indexes load into memory.
- Source identity, fingerprints, metadata or stale-index detection.
- Automatic output naming within library persistence APIs, cross-file transactions or interprocess writer locks.
- Batch/recursive CLI processing, stdin payloads, GUI, service or public asynchronous API.

## Design and delivery ownership

[ARCHITECTURE](ARCHITECTURE.md) defines major blocks and dependency direction; [DECOMPOSITION](DECOMPOSITION.md) defines component/API ownership; [SPEC](SPEC.md) defines precise behavior, resource limits, supported formats and acceptance. [PLAN](PLAN.md) defines delivery increments, package versions and per-phase GitHub releases with source/wheel artifacts.

Distribution metadata must contain a valid version consistent with its artifacts. Dependency constraints require actual integration evidence. Resource guarantees are defined by the contracts; no additional numeric throughput target is prescribed.
