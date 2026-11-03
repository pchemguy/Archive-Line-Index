# Line-index contract

## Canonical model and byte space

[DECOMPOSITION](../DECOMPOSITION.md) owns the canonical offset representation; [public API design](../decomposition/public-api.md) owns scanner signatures. This contract specifies their required meaning. For N lines the `array("Q")` contains N starts and one EOF sentinel, has eight-byte items and values in `0..2^63 - 1`. The first value is `0` or `3`; multiple values increase strictly; the only valid singletons are `[0]` and `[3]`. Invalid array contents raise `InvalidIndexError`.

Line i occupies `[offsets[i], offsets[i + 1])`. The final value is total indexed byte length, including any skipped initial BOM; `len(offsets) - 1` is line count. Direct scanning defines its initial stream position as local offset zero without querying or restoring a position. Source-based building indexes the original payload from byte zero.

## Line and BOM semantics

Byte `0x0A` is the only terminator and belongs to the line it ends. CRLF retains both bytes; lone CR and other byte values do not terminate lines. Consecutive LF bytes preserve empty lines. A final unterminated nonempty byte sequence is a line; a trailing LF produces no extra empty line. Empty content contains no lines.

With `skip_utf8_bom=True`, exactly one initial `EF BB BF` sequence is excluded from first-line content. The first line then starts at offset 3, and all coordinates still address the original bytes. A later BOM, incomplete initial prefix or any other encoding marker is ordinary content. BOM-only input produces `[3]`. With the option false, no bytes are excluded.

| Indexed bytes | Skip BOM | Exact offsets |
| --- | --- | --- |
| `b""` | Either | `[0]` |
| `EF BB BF` | True | `[3]` |
| `EF BB BF` | False | `[0, 3]` |
| `b"abc"` | Either | `[0, 3]` |
| `b"abc\n"` | Either | `[0, 4]` |
| `b"abc\r\n"` | Either | `[0, 5]` |
| `b"abc\rdef"` | Either | `[0, 7]` |
| `b"\n"` | Either | `[0, 1]` |
| `b"\n\n"` | Either | `[0, 1, 2]` |
| `b"a\n\nb"` | Either | `[0, 2, 3, 4]` |
| `EF BB BF + b"abc\n"` | True | `[3, 7]` |
| `EF BB BF + b"\n"` | True | `[3, 4]` |

## Scanner behavior and bounds

`DEFAULT_BUFFER_SIZE` is 1 MiB. The scanner requests positive reads of at most `buffer_size`, including any initial BOM probe, and accepts arbitrary nonempty short reads. Empty bytes mean source EOF. A read result that is not `bytes`, including text or `None`, or exceeds the requested size raises `TypeError`; a nonblocking retry protocol is not part of `ReadableBinary`.

The scanner checks the first three bytes across as many legal short reads as needed, then processes content in blocks. LF search uses native block searching such as `bytes.find`, not a Python loop over individual bytes. It retains no complete line, even if a line spans arbitrarily many blocks. Working content storage is bounded by the current block and up to three probe bytes, in addition to upstream buffers and the growing offset array.

Offset coordinates and EOF are checked for overflow before an unrepresentable value is appended or returned. Failure to allocate the array raises `MemoryError`. A wrong native unsigned item size makes the representation unavailable and raises `InvalidIndexError` before scanning begins. Direct input remains open after every outcome. A read exception propagates and returns no partial array; source-based building additionally closes its owned stream.

A `ContentStream` scan proceeds to validated terminal EOF, including late archive checks. Reaching an LF or an apparent member byte count is not sufficient to complete an index. Structural validation cannot prove that an index corresponds to an external source, and no identity is stored.

## Acceptance

- IDX-01: Every example yields the exact array, type code, item size, line count and EOF sentinel.
- IDX-02: BOM split after byte one/two, CRLF split across blocks, LF at either block edge, tiny buffers and legal short-read patterns preserve results.
- IDX-03: Incomplete/later BOMs and lone CR remain ordinary content; zero-length and BOM-only cases preserve their distinct sentinel meanings.
- IDX-04: A long line does not cause line-sized accumulation; requested reads remain bounded and scanning uses block search rather than Python per-byte iteration.
- IDX-05: Direct stream borrowing, caller read errors, invalid read results, offset overflow and allocation failures return no partial array and follow the stated error/ownership rules.
- IDX-06: Completed-array validation accepts scanner output and rejects empty arrays, wrong representations, invalid first offsets/singletons, duplicate/decreasing values and values beyond the shared range.
