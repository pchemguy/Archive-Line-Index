Archive Line Index 0.3.0 adds single-payload ZIP and sequential TAR indexing to the library and paired-output CLI, including gzip, bzip2 and xz TAR filters.

## Highlights

- Stream and index a sole regular payload from ZIP, plain TAR, `.tar.gz`/`.tgz`, `.tar.bz2`/`.tbz`/`.tbz2` and `.tar.xz`/`.txz`. Supported signatures also identify unconventional filenames and take precedence over conflicting suffixes.
- Preserve the original uncompressed payload's byte coordinates, LF/BOM rules and EOF sentinel. The same library and console/module/imported CLI interfaces produce equivalent SQLite and raw indexes for plain, ZIP and TAR sources.
- Accept empty or nested regular payloads and directory entries without extracting member paths. Reject additional files (including metadata files), links and special entries; detected ZIP encryption and unavailable selected codecs remain unsupported.
- Validate ZIP member integrity and TAR entries after the payload before successful terminal EOF. Damaged TAR headers/end markers, additional late members and compression-trailer failures cannot yield a completed index or CLI output pair.
- Preserve ordinary source filesystem errors, dependency causes, bounded reads, early closure and cleanup retry. The README now includes executable ZIP/TAR examples and a concise source-linked explanation of the native bytes.find line-boundary scan.

## Installation and downloads

Requires Python 3.11 or later. Releases now attach stable version-free bundles: `archive-line-index-wheel.zip`, `archive-line-index-source.zip` and `SHA256SUMS`. Each ZIP contains exactly one valid native Python package; its internal filename and metadata retain version identity. Verify the downloaded bundle against SHA256SUMS, then extract and install:

```bash
python -m zipfile -e archive-line-index-wheel.zip .
python -m pip install archive_line_index-0.3.0-py3-none-any.whl
archive-line-index data/records.zip
python -m archive_line_index data/records.tar.gz --output results/custom
```

The source bundle contains `archive_line_index-0.3.0.tar.gz`, which independently rebuilds the wheel. This changes the attached download filenames from previous releases; existing published tags/assets remain intact. The complete hosted inventory is independently checked for prohibited version notation, safe bundle/native contents, metadata agreement and checksums. Declared runtime dependencies install normally; no development tools or separate archive program are required for installed use.

## Behavior and compatibility

Existing plain-file, borrowed-reader, persistence and CLI signatures remain available. Archive indexes describe uncompressed payload bytes, not archive-container positions. The default output stem removes only the final suffix: `records.zip` produces `records.sqlite3`/`records.u64`, while `records.tar.gz` produces `records.tar.sqlite3`/`records.tar.u64`. An explicit shared output stem and overwrite flag retain their existing behavior; parent directories must already exist.

SQLite and raw publication remain independent. Input validation or archive integrity failure occurs before publication; if a later writer fails after SQLite succeeds, that SQLite file remains and the diagnostic identifies it. Early stream closure releases owned resources but does not claim full archive validation.

## Verification and limitations

Verification passes 574 tests with 96% production statement/branch coverage, Ruff lint/format and strict type checks. Actual native-wheel and independently source-rebuilt installations exercise console, module and imported commands, every required TAR suffix, empty and late-invalid archives, persistence pairs and all seven README examples outside the checkout. Isolated builds and independent complete-inventory/content/checksum checks pass, including all 38 shared naming-vector cases and matching faulty expected names.

Runtime checks ran on Linux with CPython 3.12.14. Native Windows, macOS, Python 3.11 and big-endian execution remain unverified. ZIP/TAR integrity checks are those observable through the supported standard-library paths, not cryptographic authenticity. Inputs must remain stable during an operation. 7z payload delivery remains planned and is rejected explicitly; multi-payload archives, password prompting and filesystem extraction are outside the supported interface.
