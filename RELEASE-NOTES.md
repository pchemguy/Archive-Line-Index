Archive Line Index 0.4.0 adds single-payload 7z streaming and indexing, completing the supported archive formats through the library and paired-output CLI.

## Highlights

- Stream a sole regular 7z member without extracting member paths or retaining the whole payload in package buffers. Empty and nested payloads are supported; extra files, links and special entries are rejected.
- Build canonical LF/BOM byte-offset arrays and matching SQLite/raw outputs from 7z using the existing library, console, module and importable CLI interfaces. CRC, extraction and terminal-size failures cannot yield a completed index or start output publication.
- Use one non-daemon extraction worker and bounded callback transport. Early close, consumer exceptions and interruption cancel package waits, release resources and join the worker. Failed reads retain their error rather than becoming successful EOF; cleanup failures preserve primary exceptions and permit close retry.
- Document every supported format with eight executable README examples and retain the source-linked explanation of blockwise bytes.find line scanning.

## Installation and compatibility

Requires Python 3.11 or later. The 7z runtime dependency is now constrained to `py7zr>=1.1.4,<1.2`, tested with 1.1.4. No development tools or separate archive executable are needed for installed use. Plain, ZIP, TAR and persistence behavior and public signatures remain available; 7z loads its dependency only when selected.

Download `archive-line-index-wheel.zip`, `archive-line-index-source.zip` and `SHA256SUMS`. Verify the bundles against SHA256SUMS, then extract and install the native wheel:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.4.0-py3-none-any.whl
archive-line-index data/records.7z
python -m archive_line_index data/records.7z --output results/custom
```

The source bundle contains `archive_line_index-0.4.0.tar.gz`, which independently rebuilds the wheel. Hosted names remain stable and version-free; valid native package filenames and metadata inside the bundles carry version identity. The complete inventory is checked for safe contents, metadata agreement and checksums.

For `records.7z`, default CLI outputs are `records.sqlite3` and `records.u64` beside the archive. Only the final suffix is removed. Parent directories must exist; existing outputs require `--overwrite`, and source aliases remain protected. One scan feeds SQLite then raw. If the second writer fails after SQLite succeeds, the SQLite output remains and the diagnostic identifies it; the pair has no cross-file transaction.

## Verification and limits

All 687 tests pass with 95% production statement/branch coverage, plus Ruff and strict type checks. Native-wheel and independently source-rebuilt installations exercise all supported formats, all three CLI routes and all eight README examples outside the checkout. Actual 7z checks cover LZMA2/COPY/deflate/bzip2, slow-consumer progressive delivery, bounded queue occupancy, empty content, full-queue early close, CRC/truncation, cleanup retry and real SIGINT.

Runtime verification is Linux/CPython 3.12.14 with py7zr 1.1.4. Native Windows/macOS/Python 3.11/big-endian execution remains unverified. Package transport uses one queued block and one current consumer block of at most 1 MiB each; dependency decompressor/callback allocations are separate. Package waits check cancellation at 0.05-second intervals, but dependency operations can delay close, so no total close-latency guarantee is made. Early close does not claim archive integrity. Inputs must remain stable, integrity checks are those available through supported dependencies, and encrypted/multi-payload archives remain outside scope.
