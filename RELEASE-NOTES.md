Archive Stream 0.5.2 is the first release under the `archive-stream` distribution and `archive_stream` Python package names. It provides one interface for reading payload bytes from plain files and supported single-payload archives, with automatic format detection and decompression.

## Highlights

- The README leads with a bounded streaming example that reads a compressed ZIP through validated EOF. Line indexing remains available independently, and the checkout demos exercise both the Python API and CLI across six formats.
- Release validation now verifies that the console command in the wheel and the declaration in the source distribution match the project configuration before writing checksums.

## Compatibility

Use `archive_stream` for Python imports and `python -m archive_stream` for module execution. Configure indexing progress on `archive_stream.scanner`. The `archive-line-index` console command still writes the same SQLite and raw binary index formats.

If the previous `archive-line-index` distribution is installed in the target environment, uninstall it before installing `archive-stream` because both provide the same console command.

## Installation

Requires Python 3.11 or later and `py7zr>=1.1.4,<1.2`. Download `archive-stream-wheel.zip` and `SHA256SUMS`, compare the bundle's SHA-256 with the manifest, then extract and install the wheel:

```bash
python -m zipfile -e archive-stream-wheel.zip .
python -m pip install archive_stream-0.5.2-py3-none-any.whl
```

The source bundle `archive-stream-source.zip` contains `archive_stream-0.5.2.tar.gz`. Linux verification covered the native wheel and a wheel rebuilt from that source distribution using CPython 3.12.14 and py7zr 1.1.4. Native Windows CMD and macOS execution were unavailable.
