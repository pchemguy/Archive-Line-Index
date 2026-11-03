# Content-stream contract

## Scope and fidelity

The public stream surface is defined in [public API design](../decomposition/public-api.md); the reader and lifecycle structure are defined in [internal API design](../decomposition/internal-api.md). The common stream owns this behavior and delegates format validation to [archive adapters](archive-handling.md).

Every returned byte belongs to the original payload, in order. The stream does not decode text, remove a BOM, normalize line endings or parse records. It is readable, non-writable and non-seekable. A caller serializes operations on one stream; independent instances have independent buffers and resources.

## Reads

| Operation while usable | Required result |
| --- | --- |
| `read(n)` with positive integer n | Return `bytes` of length at most n. Nonempty short reads are legal and do not establish EOF. |
| `read(0)` | Return `b""` without source advancement, backend finalization or an EOF claim. |
| `read(n)` with negative integer n, including the default | Consume through validated EOF and return all remaining bytes; caller-requested materialization may use payload-sized memory. A late failure raises rather than returning the accumulated result. |
| `readinto(buffer)` with nonempty writable contiguous storage | Copy at most the buffer's byte capacity, return the byte count and leave the unused suffix unchanged. Capacity is measured in bytes, not the number of nonbyte elements. |
| `readinto` with zero byte capacity | Return zero without backend work or an EOF claim. |

Read sizes must be integers, excluding `bool`; other kinds raise `TypeError`. `readinto` accepts buffer-protocol objects that can be cast to a contiguous byte view; read-only, noncontiguous or incompatible objects raise `TypeError` before reading. Neither operation delivers a byte beyond a configured size limit. Rejected buffer arguments do not advance the stream.

Only an empty positive/unbounded read or zero from a nonempty `readinto` after all backend checks succeed establishes terminal EOF. Once established, subsequent data reads return empty results without repeating finalization. A zero-size operation alone never proves archive integrity.

## State and failure priority

`closed` is false until explicit/context closure completes successfully; it is true afterward. Accessing `closed` is always allowed. Data operations and context entry on a closed stream raise `ValueError` before argument validation. Capability queries on a closed stream also raise `ValueError`. `close` on a successfully closed stream is a no-op.

On a nonclosed stream, `readable`, `writable` and `seekable` return `True`, `False` and `False` respectively, including after EOF or a retained read failure. `write`, `seek` and `tell` raise `io.UnsupportedOperation` when nonclosed and `ValueError` when closed.

An argument-validation failure leaves the nonclosed stream state unchanged and performs no backend work. A failure during backend delivery, size enforcement, terminal validation or result allocation places the stream in FAILED and triggers owned-resource cleanup. It does not become validated EOF. The interface remains failed until explicitly closed: otherwise-valid `read`, `readinto` or context entry re-raises the retained failure, including zero-length reads. Argument validation for a nonclosed operation precedes reporting that retained failure. Resources may already be released while the interface retains FAILED and `closed` remains false. Explicit close then completes the CLOSED transition without repeating an already reported read error.

If cleanup itself cannot release a resource, the failure is surfaced and close may be retried for remaining owned resources; neither `closed=True` nor successful release is claimed prematurely. Context exit does not suppress an exception from the body. A cleanup error is attached to that primary exception; without a primary exception it is raised.

## Size enforcement

`max_uncompressed_size` is an inclusive payload-byte limit before any downstream BOM policy. `None` disables it, zero permits only an empty payload, and a payload exactly at the limit is allowed. Trustworthy declared metadata exceeding the limit causes rejection before delivery when available; accepted metadata never replaces actual-byte counting.

The common stream independently counts bytes accepted from its backend. An attempt to cross the limit raises `SizeLimitExceededError`; the triggering call returns no data and previously delivered bytes remain delivered. No excess byte is copied into a caller buffer. Reading a payload exactly at the limit through successful EOF still requires the adapter's terminal checks, so reaching the count alone does not establish completion.

Package-controlled bounded reads never fetch the complete remaining payload solely to satisfy a small request. Dependency-internal decompressor allocations remain distinct from this delivery limit. A backend cannot evade actual-size enforcement through inaccurate metadata.

## Close and producer outcomes

Successful close releases every package-owned source, archive, member handle, buffer and extraction worker. Closing early abandons unread validation and does not itself report an undiscovered decompression failure. A failure already raised by a read is retained for that read; cancellation-only internal exceptions do not escape as `ExtractionError`.

For 7z, close signals cancellation independently of the queue, wakes package-controlled capacity/data waits, stops accepting callback blocks, lets worker-owned resources unwind and joins the thread before returning successfully. Queue operations check cancellation at intervals no greater than 0.1 seconds; this bounds package-controlled waiting, not dependency calls, scheduling or overall close latency. No package-owned thread remains alive after successful close.

Producer data, success and failure remain distinct. Already queued bytes may be returned by bounded reads before a pending producer failure is exposed; the next read needing producer progress raises it instead of EOF. A read that exposes a failure returns no partial result from that call. The unbounded-read rule above applies even if valid prefixes were accumulated internally.

The default 7z queue capacity is one payload block and each block is at most 1 MiB. An active callback can retain its dependency-supplied buffer and one block being transferred; the consumer and common stream can retain their current blocks. These finite package-controlled buffers must not grow with total payload size. Numeric policy is internal and is not a public tuning API.

## Acceptance

- STR-01: All source formats reproduce exact payload bytes under short, zero, bounded, unbounded and readinto requests; buffer tails remain unchanged and byte-capacity handling covers nonbyte buffer elements.
- STR-02: Zero-size operations do not advance or force terminal validation; positive reads surface late validation failures rather than returning EOF.
- STR-03: Limits at zero, exact payload size and one byte below size distinguish allowed, rejected and validated-EOF outcomes, independently of metadata.
- STR-04: Read failure is retained, no later data read reports successful EOF, invalid/closed-state precedence matches this contract and repeated successful close is harmless.
- STR-05: Early close, consumer exception and producer failure release resources; full-queue and waiting-reader cancellation complete without a package-controlled deadlock or surviving owned thread.
- STR-06: A slow consumer cannot make transport occupancy exceed the finite policy; generated payloads are delivered before producer EOF without whole-payload retention by package buffers.

## Internal provider obligations

The backend reader accepts positive integer read sizes, rejecting booleans/nonintegers with `TypeError` and nonpositive values with `ValueError` before acquisition progress. Each result is `bytes` of at most the requested size. An empty result requires `completed=True`; a failure must not set successful completion. After completed exhaustion, later positive reads stay empty. Reader close releases its owned resources and is idempotent after successful release. The common stream treats a violated reader result/completion contract as `ExtractionError` and cleans up.

The 7z bridge validates a callable producer and positive finite integer queue/block sizes before starting its worker; invalid kinds and values raise `TypeError` and `ValueError` respectively. The producer returns once for success or raises for failure, with one terminal outcome following its queued data. Cancellation used for close does not enqueue a success outcome. These internal checks are verification seams, not additional public APIs.
