# Line-index specification

## 1. Scope

This specification defines byte-line semantics, UTF-8 BOM treatment, the canonical in-memory offset representation, structural validation, the scanning algorithm, edge cases, and completion behavior.

The scanner consumes a readable binary stream and does not know whether bytes came from a plain file, archive backend, or another caller source. Stream ownership and archive completion are defined in [content-stream.md](content-stream.md); public functions are defined in [public-api.md](public-api.md).

## 2. Indexed byte space

For `build_line_index(source)`, offsets are relative to the beginning of the plain file or decompressed archive member, including any leading BOM bytes.

For `scan_line_offsets(stream)`, the stream's position when scanning begins is defined as local offset zero. The result indexes the byte sequence from that position through EOF. The function neither queries nor depends on an external absolute file position.

All offsets are physical byte positions in the indexed byte sequence. BOM exclusion changes the first stored line start but does not renumber later bytes.

## 3. Byte-line definition

Byte `0x0A` is the only line terminator.

- A terminating LF is included in its line's half-open range.
- CRLF contributes both bytes to that range.
- A lone CR does not terminate a line.
- Consecutive LF bytes represent consecutive empty lines.
- A final nonempty byte sequence without LF is a line.
- EOF immediately after LF does not create an additional empty line.
- An empty byte sequence contains no lines.

The package does not decode content, recognize Unicode line separators, or use `str.splitlines()`/`bytes.splitlines()`, whose boundary rules are broader than this contract.

## 4. UTF-8 BOM policy

With `skip_utf8_bom=True`, exactly one leading byte sequence `EF BB BF` is excluded from line content.

- Only bytes at indexed offset zero are considered.
- Detection works even when the three bytes cross arbitrary read boundaries.
- An incomplete BOM prefix at EOF is ordinary content.
- `EF BB BF` appearing later is ordinary content.
- No UTF-16, UTF-32, or general encoding detection is performed.
- Offsets remain relative to the original indexed bytes: the first line starts at `3`, not at a renumbered `0`.
- BOM-only input contains no lines and has the sole EOF sentinel `3`.

With `skip_utf8_bom=False`, all bytes are ordinary content. A BOM-only input is one unterminated line with offsets `[0, 3]`.

## 5. Canonical in-memory representation

The index is an `array("Q")` whose items are unsigned 64-bit integers. The runtime must report `itemsize == 8`; otherwise the platform is unsupported.

For `N` lines, the array contains exactly `N + 1` values:

```text
offsets[0]       start of line 0
offsets[1]       start of line 1
...
offsets[N - 1]   start of line N - 1
offsets[N]       indexed EOF sentinel
```

For every valid line number:

```python
start = offsets[line_number]
end = offsets[line_number + 1]
length = end - start
```

The EOF sentinel is not a line. Therefore:

```python
line_count = len(offsets) - 1
indexed_size = offsets[-1]
```

The use of starts plus one sentinel avoids storing lengths while providing constant-time derivation of every line's range, including the last line.

## 6. Structural validity

A valid offset array satisfies all of the following:

1. Its concrete type is `array` with type code `"Q"` and item size eight.
2. It contains at least one value.
3. Its first value is `0` or `3`.
4. Every value is in `0..2^63 - 1`, the range shared with SQLite `INTEGER`.
5. If more than one value exists, values are strictly increasing.
6. The final and maximum value is interpreted as EOF.

The first value `3` structurally represents an excluded leading UTF-8 BOM. A persisted index intentionally contains no source bytes or metadata with which to re-prove that the original payload actually began with the BOM.

An array with one value is a zero-line index. `[0]` represents empty indexed content; `[3]` represents a skipped BOM-only sequence. Other sole values are invalid.

Validation cannot prove that offsets correspond to a particular external payload. Source identity and stale-index detection are outside scope.

## 7. Required examples

| Indexed bytes         | `skip_utf8_bom` | Offsets        | Lines |
| --------------------- | --------------: | -------------- | ----: |
| `b""`                 |          either | `[0]`          |     0 |
| `EF BB BF`            |          `True` | `[3]`          |     0 |
| `EF BB BF`            |         `False` | `[0, 3]`       |     1 |
| `b"abc"`              |          either | `[0, 3]`       |     1 |
| `b"abc\n"`            |          either | `[0, 4]`       |     1 |
| `b"abc\r\n"`          |          either | `[0, 5]`       |     1 |
| `b"abc\rdef"`         |          either | `[0, 7]`       |     1 |
| `b"\n"`               |          either | `[0, 1]`       |     1 |
| `b"\n\n"`             |          either | `[0, 1, 2]`    |     2 |
| `b"a\n\nb"`           |          either | `[0, 2, 3, 4]` |     3 |
| `EF BB BF + b"abc\n"` |          `True` | `[3, 7]`       |     1 |
| `EF BB BF + b"\n"`    |          `True` | `[3, 4]`       |     1 |

## 8. Scanning algorithm

The scanner reads bounded blocks of at most `buffer_size` requested bytes. It does not assume the source honors the requested size exactly; arbitrary short reads are accepted until `b""` reports EOF.

The algorithm is:

1. Obtain at most the first three bytes, across as many nonempty short reads as required, solely to decide the UTF-8 BOM policy.
2. Replay non-BOM prefix bytes into normal scanning.
3. Set `line_start` to `3` when a BOM is skipped, otherwise `0`.
4. Maintain `stream_end`, the absolute offset immediately after all bytes read.
5. For each block, repeatedly call `block.find(b"\n", search_from)`.
6. For every LF found, append the current `line_start` and set `line_start` to the absolute byte immediately following that LF.
7. Advance `stream_end` by the complete block length, including bytes after the last LF.
8. At EOF, append `line_start` if `line_start < stream_end`, representing a final unterminated line.
9. Append `stream_end` as the EOF sentinel.
10. Validate the resulting array before returning it.

No Python loop examines each content byte. Iteration occurs over blocks and LF matches; `bytes.find()` performs each byte search in native code.

The scanner does not assemble line content. A line may span any number of blocks without memory proportional to line length.

## 9. Read and failure behavior

`buffer_size` controls requested scanner reads, not archive-backend chunk sizes. The scanner shall handle:

- a BOM split after either the first or second byte;
- an LF at the beginning or end of a block;
- CR and LF split across blocks;
- arbitrarily many blocks without LF;
- empty short reads only when they represent the stream's declared EOF under Python binary-I/O semantics.

If any read raises, the exception propagates and no offset array is returned. If the input is `ContentStream`, the scan continues until successful terminal EOF, thereby including late archive structure and integrity validation.

The caller-provided stream remains open after direct scanning. The composed `build_line_index()` operation closes its `ContentStream` in all cases.

## 10. Memory and numeric limits

The offset array uses exactly eight payload bytes per line plus eight bytes for the sentinel, excluding the small Python `array` object overhead and allocator capacity.

Scanner working memory is bounded by:

- the offset array;
- one requested scan block;
- at most three BOM-probe bytes;
- small integer/search state;
- upstream stream/backend buffers.

The longest line does not add line-sized scanner storage.

The maximum supported indexed size and offset is `2^63 - 1` so every value can be persisted as SQLite `INTEGER`. The scanner raises `InvalidIndexError` before appending or returning a value outside that range.

## 11. Acceptance conditions

The line index conforms when:

1. Every required example produces the exact stated sequence.
2. Results are invariant under every tested read-block boundary and arbitrary legal short-read pattern.
3. The scanner uses native block searching rather than Python per-byte iteration.
4. A line larger than the scan buffer adds no full-line accumulation.
5. Direct scanning does not close the supplied stream.
6. Composed archive scanning does not return before successful terminal validation.
7. Invalid buffer sizes and numerically unrepresentable offsets fail through the public validation/error contract.
8. Structural validation accepts every scanner-produced array and rejects empty, wrongly typed, nonmonotonic, duplicate, invalid-first-offset, and out-of-range sequences.
