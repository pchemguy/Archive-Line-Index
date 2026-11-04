# Comprehensive code and documentation review

Campaign 005_544c112; exact starting/reviewed baseline 544c11280b807fd03c158023c5563dda5d453e34. Working branch revision/005_544c112-code-docs; creation parent/target main. [Plan](REVIEW-PLAN.md) defines coverage, criteria, authorization and evidence limits. Open: U-001 and U-002 assessed; U-003 remains planned. Linux/CPython 3.12 execution is available; native Windows execution is not available. Important confirmed repairs and closure are authorized, followed by a separate patch release.


## U-001 — Runtime and contracts

Reviewed product source is unchanged from 544c11280b807fd03c158023c5563dda5d453e34. Inspected all 22 production modules, PROJECT/ARCHITECTURE/DECOMPOSITION, public/internal interface children, SPEC and all six contract children. Checked downward dependencies, strict type/value validation before acquisition, signature/suffix precedence, archive sole-member checks, terminal validation, retained stream failures, cancellation/backpressure/join ownership, LF/BOM/EOF invariants, storage encoding/schema and exclusive/replacement publication, CLI alias preflight and partial-output diagnostics. No confirmed important runtime defect was found in this unit.

Fresh baseline console pytest with --cov=archive_line_index --cov-report=term-missing passed 711 tests in 35.04 seconds at 95% production branch-inclusive coverage. This includes actual archive/codec paths, terminal corruption, producer transport/lifecycle, persistence failure injection and installed consumers; test harness depth is assessed separately in U-002. An independent fixed-seed oracle generated 1,000 byte payloads with LF/CR/NUL/high bytes, optional initial BOM and random buffers 1–19; exact scanner values matched independently calculated line starts and EOF. Eighty raw/SQLite round trips of the first 40 cases preserved exact arrays. These probes were executed, not merely read.

No-finding coverage is bounded by inspected paths and these scenarios; it does not prove arbitrary corruptions or native Windows behavior. Stable sources and serialized operations remain documented assumptions; dependency-internal decompressor allocations and fixed close latency remain explicitly outside bounded-buffer guarantees. The prospective next units may identify cross-component issues despite this no-finding result. This unit's evidence is persisted in its containing commit and published/read back before U-002.


## U-002 — Verification and distribution tooling

Reviewed source remains the starting baseline. Inventoried all test modules and inspected fixtures/helpers, entry-point and installed-consumer harnesses, artifact/bundle/name checks, shared name vectors, and focused lifecycle/scanner/publication failure scenarios. Baseline execution covered all 711 collected cases, not only integration tests. Inspected all four script modules and pyproject build/tool definitions; no CI workflow is present. Current real builds and sdist-rebuilt installed consumers passed. Ruff lint/format (74 files) and strict mypy (26 source/script files, --no-native-parser) pass. No additional unsafe self-process os.kill call was found. Two important confirmed defects follow; other inspected contract/failure coverage produced no important finding.

### R-001 — Release integration tests are pinned to 0.4.0

Type: test/release maintenance defect. Priority: Important (release verification blocker). Confidence: confirmed by execution. Baseline locations: tests/integration/test_distribution_metadata.py:14–44, test_release_artifacts.py:17–28, test_release_bundles.py:20–69 and test_installed_package.py:21. Native paths, metadata assertions, release tag arguments and installed metadata checks embed 0.4.0 rather than the authoritative project version. A correct patch bump makes verification fail; the inventory-fault tests fail at tag mismatch before reaching their intended fault.

An isolated git-archive copy of the exact baseline with only pyproject version changed to 0.4.1 produced eight failures across distribution metadata/native inventory/bundle tests (missing 0.4.0 filenames and tag mismatch). The reviewed checkout was not changed by this probe. Correct by deriving version/tag from project metadata in shared test support, preserving exact version checks against built/installed artifacts. Recheck the same subset and installed workflows on an isolated 0.4.1 copy, plus current-version full tests. Disposition: Accepted under the user's important-fix instruction; implementation not yet performed.

### R-002 — Rejected symlink staging directory is written before validation

Type: release producer filesystem defect. Priority: Important (unintended output mutation). Confidence: confirmed by execution. Baseline location: scripts/prepare_release.py:105–125 (prepare_bundles), compared with check_bundles's earlier directory.is_symlink rejection. prepare_bundles follows a symlink output directory, creates both ZIPs in its target, then fails when final check_bundles rejects the directory. A direct synthetic-native probe raised “Release staging requires ordinary files only” while leaving archive-line-index-source.zip and archive-line-index-wheel.zip in the external target.

Reject a symlink output directory before any producer writes or native-checksum generation. Preserve normal empty-directory construction and existing target contents; add a failure-path regression proving rejection leaves the target untouched. Recheck both the guard and actual bundle build/check workflows. This does not promise interprocess race resistance or forbid all symlink ancestors. Disposition: Accepted under the user's important-fix instruction; implementation not yet performed.

Both defects affect tests/release tooling, not payload indexing. Synthetic unit fixtures intentionally using historical version numbers are not R-001 defects; retain those useful fixed vectors. Native platform coverage remains limited to Linux; symlink regression may be unavailable where creation rights are absent and must report that honestly.
