# Test ownership

## Organization and shared support

`tests/` owns all pytest-based verification code and no production implementation. `tests/conftest.py` contains genuinely shared fixtures, with support under `tests/helpers/` for archive generation, byte corpora and controlled readable streams. Helpers create runtime archives/databases in temporary directories; package tests do not depend on checked-in large binaries or conversation records.

Markers/configuration remain in `pyproject.toml`. Integration tests that launch installed subprocesses use the relevant integration marker; platform-specific and slow cases use their declared markers. Capability-based limitations are recorded without treating skipped native execution as passing evidence. Do not create duplicate tests under root and integration paths for the same ownership subject.

## Unit and component checks

| Path/group | Implementing owner and boundaries checked |
| --- | --- |
| `tests/unit/test_sources.py`, `test_formats.py`, `test_errors.py` | Path/type checks, bounded detection/evidence precedence and public error definitions. |
| `tests/unit/test_stream.py` | Common reader substitution, bounded/zero/unbounded reads, readinto, size/count/state and cleanup behavior. |
| `tests/unit/test_offsets.py`, `test_scanner.py` | Canonical arrays, range checks, LF/BOM examples, short reads, borrowed ownership and invalid source results. |
| `tests/unit/test_api.py`, `test_package.py` | Facade composition, pre-acquisition checks, ownership transfer and explicit public exports. |
| `tests/unit/backends/test_plain.py`, `test_registry.py`, `test_zip.py`, `test_tar.py` | Adapter selection and format-specific metadata/read/finalization failures. Common stream tests do not duplicate archive internals. |
| `tests/unit/backends/test_producer.py` | Controlled producers, finite block/queue behavior, distinct terminal outcomes, cancellation and worker joining without a `py7zr` dependency. |
| `tests/unit/backends/test_sevenzip.py` | 7z metadata/callback adapter boundaries; real dependency behavior is also required in integration checks. |
| `tests/unit/persistence/test_fs.py`, `test_sqlite.py`, `test_raw.py` | Publication commit points, temporary/sidecar ownership, exact formats, corruption, byte order and injected failures. |
| `tests/unit/test_cli.py` | Importable argv handling, default/shared stems, both-path preflight, statuses, one scan, writer order and accurate partial-publication reporting. |
| `tests/unit/test_release_artifacts.py` | Development-script inventory/name/version/checksum behavior using synthetic archives; no hosted release mutation. |

## Integrated and installed behavior

| Path/group under `tests/integration/` | Composed behavior and artifact evidence |
| --- | --- |
| `test_content_stream.py`, `test_index_building.py` | Actual plain/archive corpora through public streaming and source/direct indexing, including terminal integrity and chunk-boundary equivalence. |
| `test_resource_lifecycle.py`, `test_large_inputs.py` | Real dependency cancellation/failure/close, no surviving package worker, progressive delivery and separation of index growth from package buffering. |
| `test_persistence_equivalence.py`, `test_filesystem_publication.py` | Exact SQLite/raw equivalence and real filesystem protection/replacement/cleanup behavior, with simulated unavailable primitives isolated in unit checks. |
| `test_cli.py` | Console/module/imported paths, generated paired outputs, input aliases, writer failure/interruption and no import-time work. |
| `test_installed_package.py`, `test_distribution_metadata.py` | Build/install outside the checkout, delivered exports/entry points, source-distribution rebuild, runtime dependency boundary and native artifact inventory. |
| `test_documentation_examples.py` | Executable public examples against delivered behavior without copying normative contracts into documentation tests. |

Installed-artifact checks use actual built package bytes and a working directory outside the repository; they cannot pass solely through `src` path injection. Source/release inventory checks inspect native artifacts, required build inputs and exclusions. GitHub upload/download identity is release evidence under the phase release workflow, not a unit test that sends hosted mutations.

Milestone and phase review evidence follows the [document map](docs.md) and PLAN boundaries. This allocation does not prescribe a test per contract sentence or claim that any test file already exists or has passed.
