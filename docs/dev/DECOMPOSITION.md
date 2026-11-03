# Archive Line Index component design

## Scope and document ownership

[ARCHITECTURE](ARCHITECTURE.md) defines the system arrangement. This document defines logical components, dependencies, data ownership and collaboration. [Public API design](decomposition/public-api.md) owns public types, signatures and exports. [Internal API design](decomposition/internal-api.md) owns cross-component interfaces, internal messages and lifecycle state. These three documents form one design proposal.

SPEC will define exact behavior, errors and acceptance against these interfaces. Physical module paths and delivery order belong to layout and PLAN. The component names below identify responsibilities, not a prescribed file tree.

## Component ownership

| Component | Provides and owns | Requires and excludes |
| --- | --- | --- |
| CLI adapter and execution wrappers | Importable `archive_line_index.cli.main`, one-target argument parsing, destination choice, preflight, status messages and exit-code translation; console/module wrappers invoke the same callable | Uses the index-building facade and both persistence writers through their owning modules. Owns its completed array until persistence finishes; contains no scanning, decompression or storage implementation. Core modules do not import it. |
| Public facade | Supported exports and the composition of source opening with scanning; validation before opening resources; ownership transfer to the returned stream | Uses source normalization, detection, backend selection, stream construction and scanning. It contains no decompression, LF scanning or persistence encoding. |
| Source normalization | Filesystem-path validation and conversion to a `Path` | Uses normal filesystem path semantics; accepts no open stream or URL as an archive source. |
| Format detection | Bounded content inspection and recognized-suffix claims, returned as one format candidate | Borrows a normalized path, owns only its short-lived inspection handle and performs no full extraction or line analysis. |
| Backend selection | Explicit mapping from the selected format candidate to the supported adapter | Depends on concrete adapters and their shared reader contract; provides no public registration or discovery mechanism. |
| Content stream | Public read operations, bounded buffering, actual decompressed-byte accounting, size limits and closure | Owns exactly one backend reader. Depends on the reader contract rather than concrete formats; does not detect formats, interpret lines or persist indexes. |
| Plain, ZIP and TAR adapters | Opening, member validation, payload reads and terminal integrity/structure checks for their format | Own source/archive/member handles. TAR retains the sequential iterator needed for trailing validation. They implement the shared reader contract and never depend on scanning. |
| 7z adapter and bridge | Selected-member validation, callback writer, bounded transport, one extraction thread and producer outcome delivery | Owns the worker, cancellation signal and queue. Isolates `py7zr`; the callback cannot extract member paths or buffer the complete payload. |
| Line scanner | Scan-option validation, leading-BOM state, absolute byte position and offset construction | Borrows only a readable binary input; depends on the offset model and has no archive/backend dependency. |
| Offset model | Canonical offset representation, append/range checks and completed-array validation | Knows neither source paths nor encodings, except that first offset `3` structurally represents a skipped UTF-8 BOM. |
| SQLite persistence | Dedicated database schema, transaction completion, validation and ordered loading | Uses the offset model and publication helper; owns SQLite connections and statements. It does not share a transaction with raw persistence. |
| Raw persistence | Little-endian serialization, file-shape validation and array loading | Uses the offset model and publication helper; owns file handles and byte-order conversion without mutating the supplied array. |
| Filesystem publication | Unique temporary siblings, protected creation, authorized replacement and temporary-path cleanup | Uses filesystem primitives only; contains no SQLite, array or archive rules. Publication and later temporary cleanup remain distinguishable operations. |
| Shared errors | Package exception classes and stable failure categories | Has no dependency on the public facade or domain components. Boundary owners retain specific ordinary Python errors and chain translated dependency errors. |

The public facade calls lower-level providers. Source and format helpers do not import the facade or stream implementation. Concrete adapters implement the shared reader interface; the common stream consumes that interface. Scanner and persistence converge only on the offset model. Internal code imports definitions from their owner, never through public package initialization. No callback from a provider to a higher-level composition component is needed.

## Data model

| Data | Canonical owner and representation | Ownership and invariants |
| --- | --- | --- |
| Source argument | Public API design: `Source` | Caller supplies a filesystem path value; normalization returns a `Path` without transferring any open handle. |
| Format candidate | Internal API design: `FormatCandidate` and `FormatKind` | Immutable detection result retaining signature and suffix evidence; it selects an adapter but certifies no complete archive validity. |
| Payload | Adapter reader interface | Original decompressed bytes. Returned `bytes` belong to the caller; queue blocks are immutable and owned by the bridge until consumed. |
| Completed line index | Offset model: `array("Q")` with eight-byte items | For N lines, N starts plus one EOF sentinel. Values fit `0..2^63 - 1`; first value is `0` or `3`; multiple values increase strictly. The only single-value indexes are `[0]` and `[3]`. |
| Stream state | Internal API design: stream lifecycle | Buffer, backend ownership, byte count and terminal outcome are instance-local. There is no process-global active stream or shared payload cache. |
| Producer messages | Internal API design: data/completion/failure messages | FIFO payload delivery precedes the producer's terminal outcome. Cancellation uses an independent signal so a full queue cannot prevent close. |
| Persistence output | SQLite or raw adapter | An independent complete encoding of the canonical array, including EOF. No source metadata or source/index association is stored. |
| Temporary sibling | Filesystem publication helper | Created uniquely in the destination directory and owned until publication or cleanup. The destination remains caller-named. |

A newly returned index belongs to its caller. A persistence writer borrows its array and requires the caller not to mutate it during the operation. A reader creates a new array rather than sharing writable storage with the source file. Persistence validation proves structural consistency, not that offsets correspond to a particular payload.

## Collaboration

### Open content

The facade validates the size limit, normalizes the source, detects a format and asks selection to open its adapter. Selection returns an owned `BackendReader`; stream construction consumes that ownership, including cleanup if construction fails. Any failure before ownership transfer is cleaned up by the component that acquired the resource. Detection and adapter opening use separate handles, as established by ARCHITECTURE.

### Build an index

The facade validates scan options before source I/O, opens a content stream and passes it to the scanner inside deterministic cleanup. The scanner consumes short reads until validated EOF, constructs line starts in original byte space and returns its completed array. A scanning or backend failure yields no partial array. The facade closes the owned stream; direct scanner callers retain ownership of their own input.

### Stream 7z content

The adapter validates the selected member and starts one outer extraction thread. Its writer forwards callback bytes in bounded blocks, waiting for capacity with cancellation checks. The reader drains those blocks and observes producer completion or failure. On close, cancellation unblocks bridge-controlled waits, the worker unwinds and releases its archive resources, and the closing operation joins it. No detached worker or filesystem extraction is used. Dependency-internal work remains subject to the cooperative-cancellation limitation in ARCHITECTURE.

### Index a CLI target

Console execution and `python -m archive_line_index` invoke the same `main(argv)` adapter available to Python callers. The adapter parses without indexing on import, resolves one target and its output choice, checks destination protection and source/destination aliasing, calls `build_line_index` once and passes the same completed array to the SQLite writer and then the raw writer. It emits a success summary only after both writes succeed and returns an integer status. If a later write fails, already published output is retained and identified in the failure diagnostic. It does not catch library errors inside core operations or terminate a process from the imported callable.

### Persist an index

The selected writer validates the complete borrowed array, normalizes the destination and acquires a temporary sibling. It builds and checks its own format, closes format handles and invokes publication. The publication helper separates exclusive protected creation from authorized replacement; temporary cleanup follows the publication result. A pre-publication failure preserves an existing destination. SPEC must distinguish such failures from cleanup errors after a successful publication, when the new destination already exists.

## Interface readiness and verification seams

The public API child defines all supported consumer entry points. The internal child defines the boundaries needed for source selection, reader substitution, scanning, offset checks, producer delivery and publication. Private helpers with no cross-component consumer are deliberately left to implementation.

Reader doubles exercise common-stream completion and size enforcement without concrete archive dependencies. Short-read inputs exercise scanner boundaries and borrowing. A controlled producer exercises 7z backpressure, terminal outcomes and cancellation. Real archives exercise dependency integration and format-specific validation. Publication primitives can be fault-injected separately from SQLite/raw construction, while actual filesystem tests verify destination protection and replacement. Public export and installed-package checks exercise the facade rather than internal import paths.

No material structural question remains open in this proposal. SPEC must settle exact argument/error behavior, supported format variants, read-after-failure details, numeric buffering policy, dependency suitability, filesystem support and post-publication cleanup outcomes before implementation tasks rely on them.
