Archive Line Index 0.4.1 is a maintenance release improving bounded input reads, ZIP validation, SQLite publication and the reliability of development and release checks. Public library and CLI interfaces and supported formats are unchanged.

## Fixes

- Keep format inspection within a 512-byte raw-read budget, including legal short reads, and avoid implicit read-ahead in plain payload delivery.
- Reject ZIP delivery whose observable byte count disagrees with declared member size before reporting successful completion.
- Synchronize completed SQLite indexes through a writable, non-truncating handle, addressing Windows file-synchronization requirements.
- Make console pytest resolve checkout release helpers, report missing required plugins clearly and isolate SIGINT cleanup tests so a signal regression cannot terminate the test runner. Signal injection now uses signal.raise_signal instead of self-process os.kill.
- Make release integration checks follow the authoritative package version, include build/Hatchling in test setup, read project/example inputs explicitly as UTF-8 and use portable archive test IDs.
- Reject symlink bundle-staging directories before writing files into their targets.

## Installation and compatibility

Requires Python 3.11 or later and py7zr>=1.1.4,<1.2; actual dependency integration uses py7zr 1.1.4. No separate archive executable is required. This patch preserves line/BOM/EOF semantics, source/output naming, SQLite/raw formats and public signatures.

Download archive-line-index-wheel.zip, archive-line-index-source.zip and SHA256SUMS from this release. Verify the bundles against SHA256SUMS, then extract and install the native wheel:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.4.1-py3-none-any.whl
```

The source bundle contains archive_line_index-0.4.1.tar.gz and independently rebuilds the wheel. Hosted names remain stable and version-free; native package filenames and metadata inside the bundles carry version identity. For checkout development/testing, install the declared prerequisites with the same interpreter:

```bash
python -m pip install ".[dev,test]"
python -m pytest -vv
```

## Verification and limitations

The complete suite passes 713 tests with 95% production statement/branch coverage, including native builds, source-distribution rebuilds, isolated installed consumers and all eight README Python examples. Ruff lint/format and strict type checks pass. Next-version checks, symlink staging and clean test-setup fixes have observed failure-before-fix and successful rechecks.

Actual execution is Linux/CPython 3.12.14 with py7zr 1.1.4. Windows termination and synchronization requirements have targeted regression coverage, but native Windows/macOS/Python 3.11/3.14/big-endian execution remains unverified. ZIP checks cannot detect bytes hidden by the standard-library member stream. Existing cooperative 7z cancellation and independent two-output publication limitations still apply; no fixed dependency-call cancellation latency or cross-file rollback is promised.
