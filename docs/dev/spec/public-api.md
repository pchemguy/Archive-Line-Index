# Public operation and error contracts

## Surface and validation

The canonical signatures, exported types and exception hierarchy are in [public API design](../decomposition/public-api.md). The facade, source normalizer and shared error component in [DECOMPOSITION](../DECOMPOSITION.md) own these obligations.

`Source` accepts `str` or a path-like object whose filesystem representation is `str`. Bytes paths, arbitrary objects and path-like values returning bytes raise `TypeError`. Normalization performs no source opening. Empty or invalid path values retain the appropriate ordinary filesystem error when used.

| Argument | Required validation |
| --- | --- |
| `buffer_size` | Positive integer; `bool` is rejected. Wrong kind raises `TypeError`; nonpositive values raise `ValueError`. |
| `max_uncompressed_size` | `None` or a nonnegative integer; `bool` is rejected. Wrong kind raises `TypeError`; negative values raise `ValueError`. |
| `skip_utf8_bom`, `overwrite` | Actual `bool` values; any other kind raises `TypeError`. |
| `offsets` | Concrete `array` with type code `Q` and item size eight. Wrong container/type code raises `TypeError`; invalid contents raise `InvalidIndexError` under the [offset contract](line-index.md). |
| `stream` | Provides callable `read`; a missing/noncallable operation raises `TypeError` before scanning. Each read result must satisfy the scanner contract. |

All supplied option/path/array checks that need no I/O run before opening a source, starting a worker or creating a temporary file. When several arguments are invalid, no relative precedence is promised except the closed-stream rules in the [stream contract](content-stream.md). Failure to allocate memory preserves `MemoryError` after owned-resource cleanup.

## Operation outcomes

`open_content_stream` returns an owned usable stream or raises after releasing any resources acquired during failed opening. A declared oversize payload may be rejected before any public bytes are returned. Plain/archive source acquisition obeys [archive handling](archive-handling.md).

`scan_line_offsets` validates options, borrows its input from the current position and returns only a completed canonical array. It neither closes nor restores the input on success or failure. Exceptions originating in a caller's `read` propagate unchanged; a nonbinary/invalid result raises `TypeError` as defined by the scanner contract.

`build_line_index` validates all options before source acquisition, opens and owns its content stream, scans it through validated EOF and closes it on every exit. It returns the scanner's completed array only if scanning and mandatory cleanup both succeed. No index persistence or output naming occurs implicitly.

Persistence operations follow the independent [storage contract](persistence.md). Writers borrow an immutable-for-the-call array; readers own their inputs and return a new array. Input arrays and destination paths are never inferred from one another.

## Error classification

| Failure | Required public result |
| --- | --- |
| Recognized unsupported format/feature, including detected encryption or an unavailable selected codec | `UnsupportedFormatError` |
| A supported archive candidate cannot be parsed/opened as that format | `InvalidArchiveError` |
| Exposed archive entries violate the sole-regular-member policy | `ArchiveStructureError` |
| Declared or actual expanded payload exceeds the configured limit | `SizeLimitExceededError` |
| Payload decompression, CRC, footer, producer transport or terminal delivery fails | `ExtractionError`, unless a narrower category above applies |
| Offset structure or persisted index content is malformed | `InvalidIndexError` |
| SQLite engine operation fails without indicating malformed index content or a specific ordinary filesystem error | `PersistenceError` |
| Missing path, protected destination, permission/path/device failure | Appropriate ordinary `OSError` subclass, including `FileNotFoundError`, `FileExistsError` or `PermissionError` |
| Wrong argument kind or invalid ordinary option value | `TypeError` or `ValueError` respectively |
| Unsupported public stream operation | `io.UnsupportedOperation` under the stream-state rules |

Boundary owners translate dependency-specific exceptions to the narrowest applicable category and retain the original cause through exception chaining. Public messages provide useful context but their exact wording is not a compatibility contract. Filesystem failures are not disguised as malformed archive/index content. A consumer-raised exception or interruption is not relabeled as a decompression failure merely because cleanup is necessary.

No supplied password, prompting, credential discovery or extraction to member filesystem paths is permitted. Detected encryption is rejected; the package need not prove that every malformed encrypted header can be distinguished from other invalid archive content.

If cleanup fails while another exception is propagating, the original remains primary and the cleanup failure is retained as an exception note or chained context. With no primary failure, cleanup failure is raised. Successful publication followed by cleanup failure is governed separately by persistence.

## Distribution contract

The distribution is named `archive-stream`, requires Python 3.11 or later and packages `archive_stream`. It uses Hatchling and declares the required `py7zr` runtime dependency; ZIP, TAR and SQLite use the standard library. No separate archive executable or development dependency is required for installed-library use. The source distribution contains the files needed to build the wheel.

Version metadata must be present and consistent across distribution metadata and the built artifacts. Public imports work outside the checkout. Package initialization exports exactly the package-root names in the public API design and does not import optional development tools. The implementation chooses and records a dependency constraint supported by its actual integration evidence; dependency updates require rerunning affected format/lifecycle checks. The distribution also installs the console entry point and module runner defined by the public API design; both share the importable CLI callable and obey the [CLI contract](cli.md). This contract does not authorize PyPI or other external package publication.

## Acceptance

- API-01: Every documented package-root public name and the separate CLI callable import from the installed package, and internal readers, enums, worker controls and publication helpers are absent from the explicit export set.
- API-02: Invalid non-I/O arguments are rejected without opening a source, creating an output or starting a worker; normal source/path errors retain their ordinary classes.
- API-03: Composed building and direct scanning yield identical results for equivalent bytes while preserving their distinct ownership behavior, including exception paths.
- API-04: Each failure category is exercised at its owning boundary with original causes preserved for translated dependency failures; cleanup does not replace a primary exception.
- API-05: Built metadata is valid and the installed artifact completes public workflows without repository path injection, undeclared dependencies, prompts or external archive tools.
