# Content-stream specification

## 1. Scope

This specification defines the backend-independent read-only sequential stream that exposes a plain file or decompressed archive member as bytes. It owns byte delivery, buffering, decompressed-size enforcement, completion semantics, ownership, cancellation, and cleanup.

Format detection, archive structure, and backend-specific behavior are defined in [archive-handling.md](archive-handling.md). Public construction and errors are defined in [public-api.md](public-api.md).

## 2. Stream model

`ContentStream` presents one payload as a readable binary stream. It shall:

- return `bytes` from `read()`;
- support `readinto()` for writable bytes-like buffers;
- report `readable() is True` while open;
- report `writable() is False`;
- report `seekable() is False`;
- reject writing, seeking, truncation, and other unsupported mutations with `io.UnsupportedOperation`;
- implement idempotent `close()`;
- implement context management;
- follow normal Python closed-stream behavior after closure.

The stream need not expose a usable file descriptor. Position restoration and random access are not supported. Binary-I/O convenience operations inherited from the chosen base class may be available, but only `read`, `readinto`, closure, context management, and capability queries are stable public requirements.

## 3. Byte fidelity

The stream returns payload bytes without transformation.

It shall not:

- decode bytes to text;
- inspect or remove a BOM;
- translate CR, LF, or CRLF;
- parse JSONL or another record format;
- concatenate multiple archive members;
- synthesize trailing bytes.

For a plain file, the payload begins at the source stream's current position. For an archive, the payload is the full decompressed content of the selected regular member.

## 4. Read behavior

### 4.1 `read(size)`

- `size > 0` returns at most `size` bytes.
- A short nonempty result is permitted and does not by itself mean EOF.
- `b""` means terminal EOF only after all backend completion work succeeds.
- `size == 0` returns `b""` without advancing or forcing backend work.
- `size < 0` reads through terminal EOF and may materialize all remaining payload bytes in caller memory.
- Non-integer sizes follow normal Python binary-I/O validation.

The package's bounded-memory guarantee applies when callers request bounded reads. It does not override conventional unbounded-read semantics.

### 4.2 `readinto(buffer)`

`readinto()` writes no more than `len(buffer)` bytes, returns the number written, and returns `0` only at successful terminal EOF or for a zero-length buffer. A read-only or incompatible destination buffer fails through normal Python buffer-protocol exceptions.

### 4.3 Internal buffering

The implementation may buffer bytes already obtained from a backend so it can satisfy arbitrary caller read sizes. Buffering remains bounded independently of payload size. The implementation shall not read the entire payload solely to satisfy bounded reads.

The public `DEFAULT_BUFFER_SIZE` governs scanning, not a promise that every stream backend issues reads of exactly that size. Backend chunking may differ according to archive-library constraints.

## 5. Decompressed byte counting

The stream maintains an absolute count of payload bytes accepted from the backend. The count is taken before any downstream indexing policy such as BOM exclusion.

If `max_uncompressed_size` is not `None`:

1. Trustworthy member metadata declaring a larger size shall cause rejection before payload delivery when available.
2. Actual payload bytes shall be counted independently of metadata.
3. Delivery shall fail as soon as actual bytes would exceed the limit.
4. Exactly the configured number of bytes is allowed; the boundary is inclusive.
5. Bytes beyond the limit shall not be returned to the caller.

`max_uncompressed_size=0` permits only an empty payload.

Backend internal allocation that occurs before the package observes output is outside the exact byte limit, but the package shall configure dependency safety limits, where supported, so documented valid large inputs are not unexpectedly rejected.

## 6. Completion and integrity

Payload delivery and archive validation are not generally atomic. A caller may receive valid prefix bytes before a later CRC, footer, archive-structure, or decompression failure becomes knowable.

The following distinction is normative:

- A returned nonempty byte sequence proves only that those bytes were delivered successfully.
- Successful terminal `b""` proves that the backend reached logical end of the selected member and completed every integrity and trailing-structure check it can perform.
- An exception before terminal `b""` means the stream did not complete successfully, even if earlier bytes were consumed.
- Early caller closure makes no claim about unconsumed archive integrity.

For a backend that discovers additional invalid entries only after the selected member has been drained, the first read attempting to cross the logical member end performs that validation and raises instead of returning terminal `b""`.

Once successful terminal EOF has been returned, subsequent reads return `b""` without repeating backend finalization.

## 7. Source ownership

When constructed from a path, the content stream owns and closes the source file, archive object, member object, internal buffers, and any extraction worker.

When constructed from a caller-provided binary stream:

- the caller retains ownership;
- closing `ContentStream` closes archive/member wrappers and package resources but not the caller stream;
- processing begins at the stream's current position;
- consumed bytes and the final position are not restored;
- a backend library must not be permitted to close the caller stream as an accidental side effect.

Where a standard-library archive wrapper unavoidably closes only its own wrapper but not the passed file object, normal wrapper closure is sufficient. Where a dependency would close the passed object, the package shall interpose a non-closing adapter.

## 8. Closure and cancellation

`close()` is deterministic and idempotent.

Normal exhaustion, explicit closure, context-manager exit, consumer exceptions, backend failures, size-limit failures, and scanning failures shall all release the same package-owned resource set.

For a pull backend, closure closes the current member/archive wrappers and any package-owned source.

For the threaded 7z backend, closure shall:

1. set a cooperative cancellation signal;
2. unblock a producer waiting for queue capacity;
3. stop accepting callback bytes;
4. release 7z and source resources when safe;
5. join the package-owned extraction worker;
6. discard cancellation-only internal messages;
7. leave no live package-owned worker before returning.

Cancellation checks occur at bounded intervals, including every callback write, every block subdivision, and every potentially blocking queue transfer. The worker is non-daemon so deterministic cleanup cannot be bypassed by process termination semantics.

Caller-requested closure is not reported as `ExtractionError`. A genuine backend failure already observed before cancellation retains priority and is reported unless closure is being used solely to abandon the stream before that failure is delivered.

## 9. Error transport

Errors raised synchronously by pull backends propagate through the common error translation layer.

The threaded 7z adapter transports three logically distinct messages:

- a bounded payload block;
- successful terminal completion;
- failure with its exception and cause context.

Completion and failure must never share the same sentinel representation. The consuming thread raises a transported failure at the next read that needs producer progress. It must not convert an error into apparent EOF.

## 10. Thread safety and concurrency

One `ContentStream` is not required to support concurrent reads from multiple consumer threads. Callers shall serialize operations on a single stream.

The 7z producer callback, cancellation state, and queue interaction shall be safe under the threading behavior of the supported `py7zr` version. Internal synchronization shall not broaden `ContentStream` into a generally thread-safe public object.

Different stream instances are independent and may be used concurrently, subject to backend and system resource limits.

## 11. Acceptance conditions

The content-stream implementation conforms when:

1. Bounded reads return byte-identical payloads across supported formats.
2. Read sizes smaller and larger than backend chunks produce the same byte sequence.
3. Short reads, zero-size reads, `readinto()`, and unbounded reads follow the stated behavior.
4. Actual-size counting rejects the first byte beyond the configured inclusive limit.
5. Terminal backend failures are raised instead of being converted to EOF.
6. Explicit close and every exceptional path release owned resources.
7. Caller-owned source streams remain open.
8. No 7z worker remains alive after deterministic close.
9. A slow consumer cannot cause unbounded producer lookahead.
10. Streaming a large generated payload with bounded reads does not retain the entire decompressed payload.
