Archive Line Index 0.5.1 fixes memory retention after a failed read and successful stream closure, and improves integration documentation and development tooling.

## Fixes and improvements

- Release the stream's retained failure reference only after owned-resource closure succeeds. Failed unbounded reads no longer keep accumulated payload blocks alive through the closed stream. Retained errors still govern reads before closure, failed cleanup remains retryable, and externally held exceptions keep their traceback and notes.
- Align Flowmark defaults with the project's single-source-line Markdown policy; long paragraphs and list items are no longer wrapped by default.
- Update the test ownership map to the delivered modules and strengthen regression checks for close-time memory lifetime, corrupt-archive completion logging and package-import logging side effects.
- Reorganize README around library and CLI source-to-output workflows, add an Integration contract with core specification links, group backend descriptions, distinguish fixture creation from consumption, and colocate logging configuration.

## Compatibility

Public Python interfaces, automatic source-format selection, LF/BOM/EOF semantics, SQLite/raw formats, CLI output naming and status codes are unchanged. Library indexing returns an array; file persistence remains explicit. The CLI still writes both formats from one scan and defaults to INFO progress on stderr; --log-level WARNING suppresses progress. Each output is independently published, so later failures may leave an earlier output complete.

## Installation

Requires Python 3.11 or later and py7zr>=1.1.4,<1.2, tested with 1.1.4. Download archive-line-index-wheel.zip, archive-line-index-source.zip and SHA256SUMS, verify the bundle hashes, then extract and install the wheel:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.5.1-py3-none-any.whl
archive-line-index data/events.txt
```

The source bundle contains archive_line_index-0.5.1.tar.gz and rebuilds the wheel. Hosted asset names remain stable and version-free; native package metadata and tag v0.5.1 identify the version. See README for the public integration contracts and complete examples.

## Verification and limits

The full configured suite passes 757 tests with 95% production statement/branch coverage, including the two new close-time regressions and all nine README Python examples in installed wheel/source-rebuilt environments. Ruff lint/format and strict mypy checks pass. The reproduced 20-MiB late-read failure now releases its accumulated buffers after successful close while the closed stream remains referenced. Default formatter probes preserve long paragraphs and list items. Source/wheel metadata, package contents, stable names and checksums are verified before publication.

Actual execution is Linux/CPython 3.12.14 with py7zr 1.1.4. Native Windows/macOS/other Python/big-endian execution remains unverified. Existing cooperative 7z cancellation, dependency-controlled allocations and observable-only ZIP validation limits remain; no new throughput or close-latency guarantee is introduced.
