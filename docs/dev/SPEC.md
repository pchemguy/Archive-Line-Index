# Archive Stream specification

## Purpose and scope

Archive Stream is a synchronous Python library for sequential payload access, LF byte-line indexing and independent index persistence. [PROJECT](PROJECT.md) owns intent and exclusions; [ARCHITECTURE](ARCHITECTURE.md) and [DECOMPOSITION](DECOMPOSITION.md) own structure. The system accepts filesystem paths to plain files or supported single-member archives and exposes original payload bytes without extracting member paths.

The complete scope includes Python 3.11 or later on Windows, Linux and macOS; unencrypted ZIP, TAR, gzip/bzip2/xz-compressed TAR and 7z; caller-provided readable binary scanner inputs; canonical offset arrays; dedicated SQLite and raw little-endian persistence; an installable distribution; an importable minimal single-target CLI and lightweight standard-logging indexing progress. Unsupported scope includes text/record parsing, random compressed seeking, encrypted content, remote sources, multiple selected payloads, source/index identity, stale-index detection, mmap/lazy indexes, automatic naming inside library persistence APIs, public asynchronous interfaces, batch/recursive CLI processing, stdin payloads, GUI and cross-file transactions.

## Terminology and system guarantees

A **payload** is the plain file's bytes or the original decompressed bytes of the archive's sole regular member. **Indexed byte space** starts at payload byte zero, or at the caller stream's current position for direct scanning. A **byte line** ends immediately after LF or at EOF for a final unterminated sequence. A **completed index** contains line starts plus one EOF sentinel and is returned only after successful exhaustion.

The system preserves byte fidelity and original offset coordinates, including when a leading UTF-8 BOM is excluded from line content. Bounded reads and scanning do not materialize the complete payload or assemble lines. The index itself occupies memory proportional to line count. Backend metadata, decompressor allocations and caller-requested unbounded reads are accounted for separately.

Successful terminal EOF is an empty result from a positive/unbounded payload read or a zero count from `readinto` with a nonempty destination, after backend validation succeeds. Zero-length operations do not establish EOF. Bytes delivered before a late failure cannot be withdrawn; a completed index cannot be returned after that failure.

Package-created resources are package-owned; direct scanner input is borrowed. Failure, ordinary completion and early abandonment must release owned resources through the documented lifecycle. The public scanner, content stream and persistence operations remain independently usable through the accepted [public surface](decomposition/public-api.md).

## Contract ownership

Each child is normative for its assigned behavior. API/type declarations remain canonical in the decomposition children; these contracts reference them without duplicating signatures. The root owns cross-system guarantees and integrated acceptance.

| Contract | Behavioral owner | Participating design components |
| --- | --- | --- |
| [Single-target CLI](spec/cli.md) | Invocation, importable execution, destination selection, output and exit statuses | CLI adapter, entry-point wrappers, index-building facade, SQLite/raw writers |
| [Public operations and errors](spec/public-api.md) | Input validation, composed operations, exports, errors and distribution behavior | Public facade, source normalization, shared errors |
| [Content stream](spec/content-stream.md) | Read operations, limits, state, completion and cleanup | Common stream, backend reader, producer bridge |
| [Archive handling](spec/archive-handling.md) | Detection, supported formats, member validation and backend obligations | Detector, selection, concrete adapters |
| [Line index](spec/line-index.md) | LF/BOM semantics, offset validation and scanner behavior | Scanner, offset model |
| [Progress logging](spec/progress-logging.md) | Five-second byte observations, disabled cost and invocation configuration | Scanner, CLI adapter, application logging handlers |
| [Persistence](spec/persistence.md) | Storage representations, readers/writers and filesystem publication | SQLite/raw adapters, offset model, publication helper |

## Operating assumptions and limits

Sources and persisted read inputs must remain stable during an operation. A caller serializes operations on one content stream and does not mutate an offset array while a writer uses it. Different library instances may be used independently. Applications serialize shared logging reconfiguration and imported CLI invocations; scan progress counters/timers are local to each operation. The package provides neither a source snapshot nor an external-writer locking protocol.

The shared offset range is `0..2^63 - 1`. An eight-byte `array("Q")` representation is required. Payload streaming alone is not restricted by the offset range unless a size limit is requested; index construction enforces the range.

Deterministic 7z closure requires cooperative progress from the dependency and operating system. Package-controlled queue waits observe cancellation and close joins the owned thread; there is no fixed latency guarantee for an uninterruptible dependency call. Required dependency/API integration and failure-path checks must pass before 7z delivery is claimed.

Native target execution is verified where facilities are available. Unavailable native execution is reported as unverified and does not remove the target from intended support or create a fabricated passing result. Package/runtime behavior must be checked on the actual available host using installed artifacts.

## Integrated acceptance

| ID | Objective condition |
| --- | --- |
| SYS-01 | Equivalent payload corpora in plain, ZIP, TAR, compressed-TAR and 7z sources yield identical bytes and offset arrays for every supported representation of each case. |
| SYS-02 | A consumer can stream without building an index, scan a read-only short-read test stream without archive imports, and persist/reload an array without opening a payload source. |
| SYS-03 | All line-index examples and chunk-boundary cases in the child contract produce their exact sequences and EOF sentinel. |
| SYS-04 | Invalid member structures, malformed/truncated supported archives and late integrity failures produce the documented errors; no completed index is returned and no member path is extracted. |
| SYS-05 | Inclusive size-limit boundaries, early close, consumer failure and producer failure leave owned resources released; no package-owned 7z thread remains after successful close. |
| SYS-06 | Generated long-line and many-block inputs are delivered incrementally. Scanner requests remain bounded; package buffers and 7z queue occupancy obey their finite policy independently of total payload size. Index storage growth matches offset count. |
| SYS-07 | SQLite ordered rows, raw little-endian values and the original canonical array are exactly equal, including empty/BOM-only indexes and the EOF sentinel. |
| SYS-08 | Existing destinations survive unauthorized replacement attempts, a destination created at publication time is protected, and every pre-publication failure preserves the previous destination. Post-publication cleanup failure follows the explicitly distinct outcome. |
| SYS-09 | Malformed stored schemas, encodings and offset sequences are rejected without returning a partial array or modifying the input file. |
| SYS-10 | Public arguments fail before avoidable acquisition/mutation; public names, supported types and failure categories match the accepted API design and contract children. |
| SYS-11 | A wheel and source distribution build with valid consistent metadata. The installed wheel exposes exactly the supported API and completes stream/index/persistence workflows outside the repository without source-path injection or undeclared runtime dependencies. |
| SYS-12 | All contract acceptance groups below have inspectable evidence, with actual host/platform limitations and dependency versions identified. Passing a focused check does not certify unexercised formats, lifecycles or native platforms. |
| SYS-13 | Installed console execution, module execution and imported CLI invocation index the same single target once into corresponding SQLite and raw destinations, with equivalent statuses, protected overwrite behavior, accurate partial-publication diagnostics and no import-time execution. |

The companion [SPEC review](SPEC-REVIEW-REPORT.md) records design conformance and document readiness. It is not implementation acceptance evidence.
