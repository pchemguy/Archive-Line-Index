Archive Line Index 0.5.0 adds lightweight progress logging for large indexing jobs through Python's standard logging facility.

## Compatibility

The CLI now emits INFO progress on stderr by default. Its stdout success summary, exit statuses, index formats and public Python function signatures are unchanged. Use --log-level WARNING to suppress progress while retaining ordinary error diagnostics. Library use remains quiet unless the application enables INFO on archive_line_index.scanner.

## Progress reporting

- Report cumulative uncompressed bytes processed in the original indexed byte space, including an initial BOM. Plain files, all supported archives and borrowed binary-reader scans use the same scanner position.
- Check progress at chunk boundaries and emit periodic updates only after five seconds have elapsed, plus an exact final total after validated EOF and offset checks. Short or empty inputs may produce only the final total; blocked reads produce no background heartbeat.
- Keep logging outside the LF-match loop. Disabled progress reads no clock and formats no records; there are no per-line events, extra payload passes/copies, workers or dependencies.
- Respect application logging: named library records configure no root logger or handlers. The CLI reuses effective application handlers or owns one temporary stderr handler, restores the prior scanner level and does not accumulate handlers across repeated serialized calls. Log-level values are case-insensitive; DEBUG adds no per-line output.

A scan-complete record does not mean SQLite/raw publication succeeded. Existing source validation, cleanup, independent two-output publication and failure diagnostics remain in force. Standalone stream-only reads and row-by-row persistence progress are outside this feature.

## Installation

Requires Python 3.11 or later and py7zr>=1.1.4,<1.2, tested with 1.1.4. Download archive-line-index-wheel.zip, archive-line-index-source.zip and SHA256SUMS, verify the bundle hashes, then extract and install the native wheel:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.5.0-py3-none-any.whl
archive-line-index data/events.txt
archive-line-index data/events.txt --overwrite --log-level WARNING
```

The source bundle contains archive_line_index-0.5.0.tar.gz and independently rebuilds the wheel. Hosted artifact names remain stable and version-free; native package metadata and the release tag identify the version. See README for application-owned logging configuration and CLI suppression examples.

## Verification and limits

The full suite passes 755 tests with 95% production statement/branch coverage. Verification includes controlled five-second timing, disabled/dense-line costs, failures and configuration restoration, actual supported archive totals, all three installed CLI routes, native/source-rebuilt packages and all eight README Python examples. Ruff lint/format and strict type checks pass. Fresh whole-branch review found no Critical or Important issue.

Actual execution is Linux/CPython 3.12.14 with py7zr 1.1.4. Native Windows/macOS/Python 3.11/3.14/big-endian execution remains unverified. Applications own handler performance/error behavior and serialize shared logging reconfiguration/imported CLI invocations. Existing cooperative 7z cancellation and observable-only ZIP validation limits still apply.
