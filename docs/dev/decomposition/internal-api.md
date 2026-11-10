# Internal API and lifecycle design

## Scope and shared declarations

This document owns cross-component internal interfaces under [DECOMPOSITION](../DECOMPOSITION.md). [Public API design](public-api.md) owns `Source`, `ReadableBinary`, `ContentStream`, public defaults and public exceptions; those definitions are referenced rather than redeclared here. Signatures identify logical providers and consumers, not physical import paths. Private helpers may vary without changing these collaboration boundaries.

## CLI collaboration

The CLI adapter calls the existing `build_line_index` facade and `write_sqlite_index`/`write_raw_index` providers directly from their owning modules. It owns argument parsing and result presentation and receives no private scanner/backend handle. Entry-point wrappers call the public CLI `main` signature; there is no additional cross-component execution API. Destination naming is confined to the adapter. CLI preflight uses path metadata to reject source/output aliases and protected existing destinations, while the persistence provider remains responsible for publication-time protection.

## Source selection

```python
class FormatKind(Enum):
    PLAIN = "plain"
    ZIP = "zip"
    TAR = "tar"
    SEVEN_Z = "7z"


@dataclass(frozen=True)
class FormatCandidate:
    kind: FormatKind
    signature_kind: FormatKind | None
    suffix_kind: FormatKind | None


def normalize_source(source: Source) -> Path: ...
def detect_format(path: Path) -> FormatCandidate: ...
def open_backend(path: Path, candidate: FormatCandidate) -> BackendReader: ...
```

Source normalization provides `normalize_source` to the facade and persistence adapters. Detection owns `FormatKind` and `FormatCandidate`, and provides `detect_format` to the facade. The candidate retains separate content and suffix evidence; the detector resolves their precedence under SPEC and sets `kind`. A claimed malformed archive must not become an ordinary plain file. Recognition of an unsupported format raises the public unsupported-format error rather than inventing another supported enum value.

Backend selection provides `open_backend` to the facade and consumes the candidate. Concrete adapter entry points are `open_plain_backend(path: Path)`, `open_zip_backend(path: Path)`, `open_tar_backend(path: Path)` and `open_7z_backend(path: Path)`, each returning an owned `BackendReader`. Each adapter validates its format and owns acquired handles; detection does not validate or instantiate member objects for it. Backend-opening failure releases resources before returning an error.

## Backend reader and common stream

```python
class BackendReader(Protocol):
    @property
    def declared_size(self) -> int | None: ...

    @property
    def completed(self) -> bool: ...

    def read(self, size: int, /) -> bytes: ...
    def close(self) -> None: ...


def validate_stream_limit(max_uncompressed_size: int | None) -> None: ...


def make_content_stream(
    reader: BackendReader,
    *,
    max_uncompressed_size: int | None,
) -> ContentStream: ...
```

The reader-contract component owns `BackendReader`; concrete adapters implement it and the common stream consumes it. A bounded positive read returns at most the requested bytes. Empty bytes mean validated terminal completion and require `completed` to be true. `declared_size` is either trustworthy payload-size metadata or unknown; actual size counting remains with the common stream.

The common stream provides option validation and construction to the facade. Validation runs before the facade opens sources. `make_content_stream` consumes ownership of its reader at entry and closes it on construction failure. Stream instances own their buffer, accepted-byte count, size limit and terminal outcome. Backend completion does not itself mean EOF was returned to the public caller: buffered bytes may still need delivery.

The stream lifecycle is OPEN, EOF, FAILED or CLOSED. EOF records validated exhaustion; FAILED retains the failure outcome rather than converting it to EOF; CLOSED records resource release. Close is idempotent for successfully released resources and is allowed from every live state. State-dependent public error behavior and cleanup-failure handling belong to SPEC.

## Scanning and offset validation

```python
def validate_scan_options(*, skip_utf8_bom: bool, buffer_size: int) -> None: ...
def validate_offsets(offsets: array[int]) -> None: ...
def append_offset(offsets: array[int], value: int) -> None: ...
```

The scanner owns `validate_scan_options`, used by both direct scanning and the source-based facade before I/O. The offset component owns `validate_offsets` and `append_offset`. Persistence readers/writers use completed-array validation; the scanner and persistence readers use append/range checking during construction. Construction helpers cannot publish an incomplete array as a completed index. Completed-array validation enforces the canonical representation and structural invariants, not payload correspondence.

Scanner-local state consists of initial-prefix/BOM detection, absolute byte position, candidate line start and the result array. It retains only the initial prefix and current read block, never assembled line content. Public `scan_line_offsets` is the scanner's provided entry point; no separate private scanner API or archive dependency is needed.

## 7z producer bridge

```python
@dataclass(frozen=True)
class DataBlock:
    data: bytes


@dataclass(frozen=True)
class Finished:
    pass


@dataclass(frozen=True)
class Failed:
    error: BaseException


ProducerMessage = DataBlock | Finished | Failed


class QueueProducer(Protocol):
    def send(self, data: bytes | bytearray | memoryview, /) -> int: ...
    def check_cancelled(self) -> None: ...


def start_queue_reader(
    producer: Callable[[QueueProducer], None],
    *,
    declared_size: int | None,
    queue_capacity: int,
    block_size: int,
) -> BackendReader: ...
```

The 7z bridge owns the message types, producer endpoint and `start_queue_reader`. The 7z extraction adapter is its only production consumer. It supplies the extraction callable and positive finite buffering parameters; the bridge starts one worker, subdivides callback data into bounded immutable blocks and exposes its reader. Returning from the callable generates `Finished`; a failure generates `Failed`, except for bridge-internal cancellation during requested close. The endpoint does not let callback code declare premature success.

The extraction worker owns the archive during extraction and closes it while unwinding. Before the worker starts, the opening adapter owns any acquired archive; ownership transfers only once startup succeeds. Callback writer position/counter state belongs to the adapter, not the common stream. The callback forwards bytes rather than materializing a member file.

The producer has one terminal outcome: success, failure or cancellation. A separate cancellation event is observable while waiting for queue capacity or data; close does not depend on enqueueing a sentinel into a full queue. Failure and successful completion retain FIFO ordering after already queued data. Close signals cancellation, releases bridge waits and joins the worker before reporting resource release. No thread-kill, subprocess or detached-worker fallback is part of this interface. SPEC determines exact partial-read/error delivery and dependency cancellation checks.

## Filesystem publication

```python
def temporary_sibling(destination: Path) -> ContextManager[Path]: ...


def publish_index_file(
    temporary: Path,
    destination: Path,
    *,
    overwrite: bool,
) -> None: ...
```

The filesystem publication component provides these operations to both persistence adapters. `temporary_sibling` creates and owns a unique temporary path in the destination directory, closes its allocation handle before yielding and removes the remaining temporary path on exit. The format adapter owns handles it subsequently opens and must close them before publication.

`publish_index_file` performs publication only; it does not mix successful publication with later temporary-path cleanup. For protected creation it uses an exclusive publication primitive that fails when the destination already exists; for replacement it uses same-filesystem atomic replacement. A platform/filesystem without the required primitive reports failure without a weaker overwriting fallback. The outer temporary context performs cleanup even after publication failure and tolerates a temporary path consumed by successful replacement.

The caller can therefore distinguish a publication failure from a cleanup failure after publication returned successfully. SPEC defines the surfaced errors and post-publication outcomes. No locks, cross-output transaction or temporary-path callback into a persistence adapter is required.

## Progress observation and invocation configuration

Scanner-local observation consumes the existing processed-byte position, retains per-operation monotonic interval state and emits through archive_stream.scanner. It does not require a new cross-component protocol, payload callback or worker. Exact private helper shape remains implementation-owned; disabled observation performs no clock/record work and the LF-search provider has no logging call.

The CLI configures the emitting scanner logger through Python logging, not a private scanner method. It snapshots/restores that logger's explicit level and owns a temporary current-stderr handler only if no effective handler exists. Existing application handlers and root/parent/propagation/disabled settings remain untouched. Selecting the actual emitting logger ensures suppression even when it had an explicit INFO level. Repeated configuration is serialized by the embedding application. No persistence or adapter contract changes.
