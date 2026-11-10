# Streaming-first revision plan

## Campaign context

| Field | Value |
| --- | --- |
| Campaign | `011_b42b9ee` |
| Status | Open |
| Working branch | `revision/011_b42b9ee-streaming-first` |
| Creation parent and integration target | `main` |
| Baseline and branch-off commit | `b42b9ee8b87ba69430c0ded6e5c6edf9384c8a17` |

## Direction

Present sequential archive payload streaming as the library's primary capability and line indexing as a supporting capability. Downstream processing needs both. Assess how the README can lead with the public stream API, then explain how consumers use the line index alongside the stream.

Consider whether the existing project and package name still fits. Distinguish the displayed name, distribution name, Python import path and CLI command so the scope and compatibility cost of any proposed rename are clear. Start from the existing public API and determine whether the revised positioning can be achieved through documentation alone.

## Accepted revision

| Action | Scope | Acceptance |
| --- | --- | --- |
| R-001 | Lead with streaming in the project brief and README. Explain independent index creation, persistence, and reuse. | The public stream is the first library workflow. Consumer documentation links to both contracts and explains sequential access, ownership, and validated EOF. The archive-stream example runs against installed artifacts. |

The application owns record parsing, multiprocessing, and shared-memory transport. A combined one-pass helper and incremental offset or persisted-index APIs are deferred until a concrete downstream need establishes their contracts. Any rename remains a separate decision. The [revision report](REVISION-REPORT.md) records the assessment and verification.

## Archive Stream rename proposal

Use **Archive Stream** for the library. Keep the established positioning: one interface streams plain files and archive payloads with automatic format and decompressor selection. Line indexing remains an independent companion.

| Surface | Current | Proposed |
| --- | --- | --- |
| Project display name | Archive Line Index | Archive Stream |
| Installed distribution | `archive-line-index` | `archive-stream` |
| Python package and source directory | `archive_line_index`, `src/archive_line_index/` | `archive_stream`, `src/archive_stream/` |
| Module and callable CLI | `python -m archive_line_index`, `archive_line_index.cli.main` | `python -m archive_stream`, `archive_stream.cli.main` |
| Console command | `archive-line-index` | `archive-line-index`, targeting `archive_stream.cli:main` |
| Scanner logger | `archive_line_index.scanner` | `archive_stream.scanner` |
| Native artifacts | `archive_line_index-<version>-py3-none-any.whl`, `archive_line_index-<version>.tar.gz` | `archive_stream-<version>-py3-none-any.whl`, `archive_stream-<version>.tar.gz` |
| Hosted bundles for the new distribution | `archive-line-index-wheel.zip`, `archive-line-index-source.zip`, `SHA256SUMS` | `archive-stream-wheel.zip`, `archive-stream-source.zip`, `SHA256SUMS` |
| GitHub repository | `pchemguy/Archive-Line-Index` | Retain the repository identity and URL. |

Proposed compatibility policy is a clean import rename. Existing Python imports, module invocations, logger configuration, and distribution requirements need to move to the new identifiers. Keep the indexing console command. Since both distributions register that command, verify and document removing the old distribution before installing the new one in the same environment. Old version tags and release assets continue to identify their original distribution. Confirm this policy before executing the cutover.

### R-002 coordinated rename

1. **Package and tooling.** Move the complete `src/archive_line_index/` tree to `src/archive_stream/`, including `py.typed`, `__init__.py`, `__main__.py`, backends and persistence. Update absolute imports, qualified names, public API docstrings, and the CLI's scanner logger lookup. Preserve the relative import graph, root exports, CLI `prog` name, flags, exit statuses, index behavior and runtime dependencies. In `pyproject.toml`, update project metadata, the console entry-point target, Hatch wheel inclusion, coverage source, and Ruff first-party imports. Audit sdist rules, pytest paths and mypy scope against the moved tree.
2. **Packaging and release checks.** Update native filename and stable bundle expectations in `scripts/prepare_release.py`. Audit `scripts/check_release_artifacts.py` for package-name derivation from metadata and preserve its independent checks. Update the active release inventory in `docs/dev/PLAN.md`, bundle checks, checksums and expected inventories together. Keep the version-free hosted-name gate over the complete asset list. Preserve the existing checkout-only demo distribution policy.
3. **Tests.** Update import and patch targets across unit and integration tests, embedded subprocess scripts, export checks, logger and `caplog` assertions, coverage invocation, and packaging helpers. Update `test_distribution_metadata.py`, installed package/CLI/archive tests, README example tests, native-artifact tests and bundle tests to cover the proposed identifiers. Preserve historical-name fixtures where they intentionally exercise a generic verifier or the old-to-new upgrade path. Keep existing behavior assertions, negative archive cases and independently derived release expectations.
4. **Consumer docs and demos.** Update README headings, imports, module CLI examples, logger names, module/source links, install instructions and coverage commands. Update `docs/demo/alphanum/demo_api.py` and `demo_cli.bat` to use the new import and module invocation. Preserve the API batch wrapper, fixture bytes, formats, CRLF rules, and output names. Keep README links for existing releases pointed at assets that actually exist. Label the installed Archive Stream workflow when its artifacts become available.
5. **Current project guidance and contracts.** Update the project brief, architecture and decomposition, public/internal API design where affected, the spec and CLI/public API/logging contracts, active PLAN and layout ownership, and AGENTS commands. Audit links, paths and tracked config. Preserve frozen campaign records and the factual evidence in completed tasks and reports. Preserve the existing `RELEASE-NOTES.md` body for v0.5.1 until preparing the next release.
6. **Cutover boundary.** Make the namespace move and coupled consumers, tests and release checks one coherent change on the campaign branch. Record verification with the change, publish and verify the campaign checkpoint, and integrate only after the approved checks pass. Treat the next version, tag and publication as a separate release decision. Prepare new release notes and rebuild wheel/source bundles from the exact approved release source at that boundary.

### Verification matrix

| Gate | Evidence required |
| --- | --- |
| Source and tooling | Run `python -m pytest` and coverage under `archive_stream`. Run Ruff lint/format on `src`, `tests`, `scripts`, and the Python demo, plus strict mypy over its configured source and release-script scope. Compare public exports, CLI behavior, scanner progress/restoration and existing regression coverage with the baseline. |
| Wheel and sdist | Build both in clean output directories. Assert metadata name and version, normalized native filenames, `archive_stream` wheel/typed inventory, console script mapping, and source/wheel equality. Build the stable bundles and run the independent content, checksum and complete-name gates. |
| Fresh installs | Install the native wheel and a wheel rebuilt from the sdist in separate runtimes outside the checkout, with no `PYTHONPATH` injection. Assert the new distribution/import and console mapping, no old package in the clean install under the proposed policy, lazy backend loading, and all three CLI forms. Run the installed README examples and plain/ZIP/TAR/7z behavior checks through both builds. |
| Upgrade and logging | Use an isolated runtime to install the old release, remove it, install the new wheel and verify the retained `archive-line-index` command resolves the new package. Exercise the new scanner logger and CLI suppression/restoration. Compare representative SQLite/raw index outputs across old and new versions. |
| Checkout demos | Run API and CLI against separate clean fixture copies with no installed project. Require matching `demo.sqlite3` and `demo.u64` paths and offsets for all six inputs. Verify both CMD launchers on Windows where available. Otherwise verify their CLI/Python commands and path/line-ending rules and record the native execution limit. |
| Reference audit | Search tracked current source, config, tests, demos, docs and release tooling for the old spelling variants. Account for each retained occurrence by its role as the console command, repository identity, prior-release reference, historical record or intentional test fixture. Check live Markdown links and protected-record path identity. |

The implementation checkpoint starts after acceptance of the naming and compatibility proposal. Any release publication follows its own authorized boundary.
