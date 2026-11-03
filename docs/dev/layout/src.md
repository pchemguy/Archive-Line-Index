# Production source ownership

## Package and public surface

All production code is allocated under `src/archive_line_index/`. The [public design](../decomposition/public-api.md) owns supported imports/signatures; this map identifies their implementation homes. Every project-owned Python module has an appropriate module docstring, with Google-style documentation for public operations.

| Path relative to `src/archive_line_index/` | Logical owner and responsibility |
| --- | --- |
| `__init__.py` | Explicit package-root re-exports from owning modules; no CLI execution, backend state or independent implementation. Exports match the delivered phase and reach the full accepted set by final delivery. |
| `api.py` | Public facade: `open_content_stream` and `build_line_index`; validates/composes providers and transfers resource ownership. |
| `sources.py` | `Source` alias and `normalize_source`; shared path normalization without archive/scanner dependencies. |
| `formats.py` | `FormatKind`, immutable `FormatCandidate`, bounded content/suffix detection and precedence. |
| `errors.py` | Public exception hierarchy; no imports from higher-level package components. |
| `stream.py` | `ContentStream`, stream-limit validation and reader-consuming construction; common buffering, count/state and cleanup behavior. |
| `scanner.py` | `ReadableBinary`, `DEFAULT_BUFFER_SIZE`, scan-option validation and `scan_line_offsets`; no archive or persistence imports. |
| `offsets.py` | Canonical-array validation and checked construction helpers; shared signed-range and structural rules. |
| `cli.py` | Public submodule `main`, argument parsing, paired destination selection/preflight, provider composition and presentation/status mapping. |
| `__main__.py` | Guarded module-execution wrapper around CLI main; import performs no execution. |

## Backend adapters

| Path relative to `src/archive_line_index/backends/` | Logical owner and responsibility |
| --- | --- |
| `__init__.py` | Internal package marker; no eager import of all concrete adapters. |
| `base.py` | Internal `BackendReader` protocol consumed by the common stream and implemented by adapters. |
| `registry.py` | Explicit `open_backend` selection using the format candidate; unsupported undelivered candidates cannot silently become plain content. |
| `plain.py` | Plain reader and its owned source handle. |
| `zip.py` | ZIP metadata/member validation, reads, integrity finalization and cleanup. |
| `tar.py` | Sequential TAR/required-filter adapter, exposed-entry policy, trailing validation and cleanup. |
| `sevenzip.py` | 7z metadata/member selection, dependency callback writer, actual extraction integration and bridge configuration. This is the sole `py7zr` import owner. |
| `producer.py` | Internal bounded queue/worker reader, message types, producer endpoint, cancellation and joining. It depends on the reader/error contracts, not on `py7zr`, scanner or facade. |

The format adapter and producer bridge have separate physical homes because callback/library integration and queue/lifecycle mechanics have different dependencies and verification seams. They remain internal collaborators of one 7z capability, with no public backend-registration surface.

## Persistence

| Path relative to `src/archive_line_index/persistence/` | Logical owner and responsibility |
| --- | --- |
| `__init__.py` | Internal package marker; public re-exports remain at the package root. |
| `fs.py` | Unique temporary sibling context, exclusive creation/replacement primitive and ownership-aware cleanup. Publication and later cleanup remain distinguishable. |
| `sqlite.py` | SQLite public reader/writer, embedded canonical schema, transaction/integrity checks, self-contained database completion and owned sidecars. |
| `raw.py` | Raw public reader/writer, little-endian encoding, shape/content validation and conversion without mutating caller arrays. |

Both persistence adapters depend on `sources`, `offsets`, `errors` and the shared publication helper. Neither imports an archive adapter, scanner or the other format's implementation. The small SQLite schema is owned inside `sqlite.py`, not duplicated in a second schema module/file. CLI imports facade and persistence providers from their owning modules; package initialization never becomes an internal collaboration dependency.
