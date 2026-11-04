# Code review report

## Campaign and assessment

- Campaign: `001_7c8c72b`; package: `001_7c8c72b-code-review`.
- Starting/reviewed code baseline and branch-off: `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`.
- Working branch: `revision/001_7c8c72b-code-review`; creation parent/return target: `main`.
- Scope and criteria: [REVIEW-PLAN.md](REVIEW-PLAN.md).
- Request and state: campaign opened on 2026-11-04; active review in progress (`U-001` completed; `U-002` through `U-007` pending).
- Evidence boundary: direct source inspection of pinned baseline `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2` plus focused execution on Windows CMD with root Python 3.14.5 (`G:\ProgramsMisc\Anaconda\LLM-CLI\Anaconda\python.exe`). Note that in the root Python 3.14.5 environment, optional `pytest-asyncio`/`pytest-timeout` plugins and `py7zr` are not installed, which produces three `PytestConfigWarning` messages under non-strict config and `import-not-found` in `mypy` only for `src/archive_line_index/backends/sevenzip.py`.
- Readiness: partial (`U-001` assessed with 1 finding `R-001`; remaining units not yet assessed).

## Coverage and findings index

| Unit | State | Evidence | Finding IDs |
| --- | --- | --- | --- |
| U-001 | Completed | Inspected `src/archive_line_index/__init__.py`, `errors.py`, `sources.py`, `formats.py`, `offsets.py`, `scanner.py`, `api.py` and `tests/unit/test_package.py`, `test_errors.py`, `test_sources.py`, `test_formats.py`, `test_offsets.py`, `test_scanner.py`, `test_api.py`, `tests/integration/test_large_inputs.py`. Executed 170 passing unit/scanner checks (`SC-001`) and Ruff lint (`SC-002`); observed `R-001` in `formats.py` buffered inspection. | R-001 |
| U-002 | Not started | Planned scope: Common stream, backend protocol and ownership. | None allocated |
| U-003 | Not started | Planned scope: ZIP and plain/gzip/bzip2/xz TAR adapters. | None allocated |
| U-004 | Not started | Planned scope: 7z adapter and bounded producer bridge. | None allocated |
| U-005 | Not started | Planned scope: SQLite/raw persistence and filesystem publication. | None allocated |
| U-006 | Not started | Planned scope: Facade, CLI and cross-format composition. | None allocated |
| U-007 | Not started | Planned scope: Packaging, release helpers, test quality and public guidance. | None allocated |

| Finding | Type | Priority | Status | Related findings |
| --- | --- | --- | --- | --- |
| R-001 | Defect | Medium | Open | None |

## Unit assessments

### U-001 — Public surface, source detection, offset model and scanner

- **C-001 (Public API, validation, source types and error categories):** Satisfied across `src/archive_line_index/__init__.py:L1-L40`, `src/archive_line_index/errors.py:L4-L33`, `src/archive_line_index/sources.py:L7-L22`, `src/archive_line_index/scanner.py:L22-L30`, and `src/archive_line_index/api.py:L14-L69`. `__all__` exports the exact 19 public symbols required by `docs/dev/decomposition/public-api.md:L120-L135` without leaking internal readers, format enums, worker controls, or `cli.main`. `normalize_source` rejects `bytes`, `PathLike[bytes]`, and non-path objects with `TypeError` before any filesystem open. Both `open_content_stream` (`api.py:L33-L34`) and `build_line_index` (`api.py:L61-L63`) validate all non-I/O options (`skip_utf8_bom`, `buffer_size`, `max_uncompressed_size`, and `source` type) before calling `detect_format` or `open_backend`.
- **C-002 (Byte fidelity, LF/BOM rules, canonical Q/eight-byte offsets and EOF sentinel):** Satisfied across `src/archive_line_index/offsets.py:L9-L62` and `src/archive_line_index/scanner.py:L32-L102`. `_validate_representation` and `validate_offsets` enforce concrete `array("Q")` instances with `itemsize == 8`, initial offset `0` or `3`, strict monotonicity, singletons restricted to `[0]` and `[3]`, and values within `0..2^63 - 1` (`MAX_OFFSET`). `scan_line_offsets` validates `callable(getattr(stream, "read", None))` and `offsets.itemsize == 8` before reading (`scanner.py:L77-L81`), probes the first 3 bytes using `min(buffer_size, 3 - len(prefix))` so read requests never exceed `buffer_size` even for `buffer_size < 3` (`scanner.py:L84-L89`), checks `check_position(end)` before appending block offsets (`scanner.py:L40-L41`), searches blocks via `block.find(b"\n", start)` without retaining lines (`scanner.py:L43-L45`), and leaves the borrowed stream open on all success and failure paths.
- **Source detection (`formats.py`):** Signature precedence over suffix claims, case-insensitive compound suffix matching (`.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz`, `.tbz2`, `.tar.xz`, `.txz`, `.zip`, `.7z`), and TAR 512-byte header checksum / non-zero prefix discrimination match `docs/dev/spec/archive-handling.md:L10-L15`, except that `detect_format` opens the inspection handle with default `io.BufferedReader` buffering (`R-001`).

## Finding records

### R-001 — `detect_format` uses default `BufferedReader` buffering instead of bounding OS reads/buffers to 512 bytes

| Field | Evidence |
| --- | --- |
| Baseline location and confidence | `src/archive_line_index/formats.py:L43-L46` and `tests/unit/test_formats.py:L69-L77` (High confidence; confirmed by source inspection and `tracemalloc` execution on Python 3.14.5). |
| Observation and consequence | `detect_format` opens the file with `with path.open("rb") as source: signature = _signature(source.read(512))`. Because `buffering` is omitted, Python creates an `io.BufferedReader` with `io.DEFAULT_BUFFER_SIZE` (which increased to 131,072 bytes / 128 KiB in Python 3.14), issuing an underlying OS read and buffer allocation up to 128 KiB instead of reading at most 512 source bytes as specified in `docs/dev/spec/archive-handling.md:L11`. `tests/unit/test_formats.py:L69-L77` did not catch this because it patched `Path.open` with an `io.BytesIO` double rather than inspecting raw I/O or buffer allocation. Combined with default buffering in `open_plain_backend`, this causes `tests/integration/test_large_inputs.py:L33-L54` (`assert peak < 128 * 1024`) to fail on Python 3.14 (`peak = 148881`). |
| Correction and dependencies | Open the inspection handle with bounded or unbuffered I/O (for example `path.open("rb", buffering=0)` with a short-read loop up to 512 bytes, or `buffering=512`) and strengthen `test_formats.py` to verify the underlying raw read/buffer bound. Coordinates with plain-reader buffering in `U-002`. |
| Objective recheck | Verify that `detect_format` allocates and reads at most 512 bytes from the underlying raw stream and that `tests/unit/test_formats.py` and `tests/integration/test_large_inputs.py` pass under Python 3.14. |
| Current disposition | Open (review-only campaign; no source repair performed). |

## Scenarios and limits

| Scenario | Setup / expected result | Evidence method / command | Observed outcome | Limits |
| --- | --- | --- | --- | --- |
| SC-001 | Run U-001 unit tests and long-line scanner memory test (`test_package.py`, `test_errors.py`, `test_sources.py`, `test_formats.py`, `test_offsets.py`, `test_scanner.py`, `test_api.py`, `test_large_inputs.py`). | `python -m pytest tests/unit/test_package.py tests/unit/test_errors.py tests/unit/test_sources.py tests/unit/test_formats.py tests/unit/test_offsets.py tests/unit/test_scanner.py tests/unit/test_api.py tests/integration/test_large_inputs.py` | 170 passed (including `test_long_line_storage_does_not_grow_with_payload` for a 32 MiB line with `peak < 128 KiB`); 1 failed (`test_plain_stream_delivers_incrementally_with_bounded_storage`, `peak = 148881 >= 131072` due to Python 3.14 128 KiB default `BufferedReader` buffer; tracked in `R-001` and `U-002`). | Root Python 3.14.5 environment lacks optional `pytest-asyncio`/`pytest-timeout` plugins (`PytestConfigWarning` emitted). |
| SC-002 | Run Ruff lint and mypy on U-001 modules. | `python -m ruff check src/archive_line_index/__init__.py src/archive_line_index/errors.py src/archive_line_index/sources.py src/archive_line_index/formats.py src/archive_line_index/offsets.py src/archive_line_index/scanner.py src/archive_line_index/api.py` and `python -m mypy ...` | Ruff passed (`All checks passed!`). `mypy` reported zero errors in all U-001 files; its `[tool.mypy] files = ["src"]` configuration failed only on `src/archive_line_index/backends/sevenzip.py` because `py7zr` is not installed in the root environment. | Full `mypy` pass over `sevenzip.py` requires `py7zr` in the active interpreter (to be assessed in `U-004`/`U-007`). |

## Opening checks and next boundary

The worktree was clean and local main matched fetched origin/main at the full baseline above. Repository-wide campaign path/ref discovery found no existing numbered reservation or active revision/feature campaign; allocated sequence 001 without reading historical closed records. Existing phase branches are completed implementation history; unrelated manual-provenance and manager branches remain untouched.

`U-001` is complete and recorded above. After committing and publishing/reading back this `U-001` report checkpoint on `revision/001_7c8c72b-code-review`, the next eligible action is `U-002` (Common stream, backend protocol and ownership).
