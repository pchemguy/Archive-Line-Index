# Test ownership

## Organization and shared support

`tests/` owns all pytest-based verification code and no production implementation. `tests/conftest.py` reserves root shared configuration; `tests/integration/conftest.py` owns session builds, source-rebuilt wheels and clean installed runtimes. Support under `tests/helpers/` owns archive generation, byte corpora, controlled readable streams and installed-process execution. Helpers create runtime archives/databases in temporary directories; package tests do not depend on checked-in large binaries or conversation records.

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
| `tests/unit/test_release_artifacts.py`, `test_release_names.py`, `test_prepare_release.py` | Native inventory/version/checksum fault checks, complete release-name contract vectors and locale-independent metadata reading; no hosted mutation. |

## Integrated and installed behavior

| Path/group under `tests/integration/` | Composed behavior and artifact evidence |
| --- | --- |
| `test_content_stream.py` | Plain public stream byte fidelity, delivery shapes and inclusive declared limits. |
| `test_zip_workflows.py`, `test_tar_workflows.py` | Actual format corpora through public source/direct indexing, detection precedence, terminal corruption and no extraction. |
| `test_sevenzip_stream.py`, `test_sevenzip_index_cli.py` | Actual 7z payload delivery, source/index/CLI composition, member policy, integrity/limit failures and cleanup. |
| `test_full_format_lifecycle.py`, `test_sevenzip_backpressure.py`, `test_large_inputs.py` | Cross-format lifecycle/limits, actual 7z backpressure/SIGINT/cancellation, no surviving package worker and bounded payload storage versus index growth. |
| `test_persistence_equivalence.py`, `test_filesystem_publication.py` | Exact SQLite/raw equivalence and real filesystem protection/replacement/cleanup behavior, with simulated unavailable primitives isolated in unit checks. |
| `test_cli.py` | Imported CLI with real source/persistence providers, output pairs and failure/interruption/publication cleanup. |
| `test_installed_cli.py` | Console/module/imported routes from native/source-rebuilt wheels, default/explicit/protected outputs, help/usage and partial-publication diagnostics. |
| `test_pytest_entrypoints.py` | Safe-path/outside-checkout collection of release tests and clear missing-plugin prerequisite failures. |
| `test_release_artifacts.py`, `test_release_bundles.py` | Actual native build/checker CLI and stable outer bundle content/name/checksum acceptance and fault rejection. |
| `test_installed_package.py`, `test_distribution_metadata.py` | Build/install outside the checkout, delivered exports/entry points, source-distribution rebuild, runtime dependency boundary and native artifact inventory. |
| `test_documentation_examples.py` | Executable public examples against delivered behavior without copying normative contracts into documentation tests. |

Installed-artifact checks use actual built package bytes and a working directory outside the repository; they cannot pass solely through `src` path injection. Source/release inventory checks inspect native artifacts, required build inputs and exclusions. GitHub upload/download identity is release evidence under the phase release workflow, not a unit test that sends hosted mutations.

Milestone and phase review evidence follows the [document map](docs.md) and PLAN boundaries. This map identifies delivered test ownership; it does not prescribe a test per contract sentence or establish passing evidence from a filename alone.

Release naming is exercised by `tests/unit/test_release_names.py` against the shared contract vectors, including matching faulty expected sets. `tests/integration/test_release_bundles.py` builds/checks actual stable bundles from native inputs and rejects inventory, content and checksum faults. `test_installed_archives.py` covers actual ZIP/TAR commands, required filters/suffixes, empty payloads and late invalid archives in clean native/source-rebuilt installations.

## Progress logging checks

`tests/unit/test_progress_logging.py` owns exact original-byte totals, controlled one-second boundaries, complete-buffer totals, binary unit rounding and no catch-up, disabled clock/record cost, LF-density-independent observation, failure/completion and per-scan state. `tests/unit/test_cli_logging.py` owns level parsing, default/suppressed progress, actual child-level control, application-handler/root preservation, repeated calls and exceptional restoration. `tests/integration/test_progress_logging.py` owns actual format totals, no duplicate standalone-stream observation and native/source-rebuilt installed console/module/imported progress/suppression/state checks. Existing installed CLI/archive tests retain result/protection/failure checks while expecting the informational stderr contract.
