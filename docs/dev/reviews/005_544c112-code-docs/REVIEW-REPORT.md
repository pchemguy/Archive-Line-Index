# Comprehensive code and documentation review

Campaign 005_544c112; exact starting/reviewed baseline 544c11280b807fd03c158023c5563dda5d453e34. Working branch revision/005_544c112-code-docs; creation parent/target main. [Plan](REVIEW-PLAN.md) defines coverage, criteria, authorization and evidence limits. Open: all three units assessed; three important defects accepted for correction and one minor recommendation deferred. Linux/CPython 3.12 execution is available; native Windows execution is not available. Important confirmed repairs and closure are authorized, followed by a separate patch release.


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


## U-003 — Current documentation and composition

Inspected README purpose/input/output/interfaces, all eight executable Python examples and the source-linked bytes.find excerpt, installation/build/release instructions, root AGENTS/disclosures/SDD notice, current governing design/contracts/PLAN and all layout children. Product/script module documentation covers all 26 modules; no missing module docstring was found. Current file-link validation covered 21 maintained root/design/contract/layout documents with no missing linked file. Baseline installed-consumer tests executed all eight complete README examples against both native-wheel and source-rebuilt installations. Public defaults, BOM/EOF/line semantics, format limits, cleanup, CLI naming/aliases/statuses and paired-output limitations match accepted contracts and inspected implementation.

Generated and third-party content is excluded; .agents is a development dependency, not product scope. Historical review, implementation/phase/manual/preparation evidence is excluded from current-validity checks. Existing release notes describe v0.4.0 and will be refreshed from complete Git coverage as part of the separately authorized release; their historical test count is not a new defect. Native platform support is distinguished from actually executed Linux evidence. Documentation composition uncovered R-003 and minor R-004 below.

### R-003 — Documented development extras omit the required build backend

Type: setup/configuration defect. Priority: Important (clean-checkout integration failure). Confidence: confirmed by clean-environment execution. Baseline locations: pyproject.toml optional dev/test groups, README Development and artifact verification, tests/integration/conftest.py built_distributions/rebuilt_wheel. The fixtures invoke python -m build --no-isolation, but Hatchling appears only in build-system.requires, which isolated installation does not retain in the caller's environment. The test extra also omits the build frontend. Installing the documented .[dev,test] into a clean temporary environment succeeds, but its no-isolation build fails with BackendUnavailable: Cannot import hatchling.build. Preinstalled tools masked this defect in the primary verification environment.

Declare build and Hatchling in test prerequisites and Hatchling alongside existing build in dev prerequisites; clarify the documented setup relationship without dumping pyproject contents into AGENTS. Reinstall declared extras in that same clean environment and run real build/installed integration checks plus final full regression. No runtime dependency changes are needed. Disposition: Accepted under the important-fix instruction; implementation not yet performed.

### R-004 — Test placement map contains obsolete planned filenames

Type: documentation recommendation. Priority: Minor. Confidence: source inspection. Baseline location: docs/dev/layout/tests.md Integrated and installed behavior refers to test_index_building.py and test_resource_lifecycle.py, while delivered coverage resides in per-format files and test_full_format_lifecycle.py. The map explicitly describes allocation rather than claiming those files exist; current tests and contract ownership are discoverable, but maintainers may follow obsolete path suggestions. A later layout maintenance pass can reconcile exact filenames and add entry-point prerequisite checks. Disposition: Deferred because this is a nonblocking allocation-document cleanup, outside the selected important-defect repair queue; it does not change accepted behavior or invalidate current tests.

## Consolidated assessment

U-001–U-003 are assessed on product baseline 544c11280b807fd03c158023c5563dda5d453e34. Three important confirmed findings R-001–R-003 require bounded correction before release verification; minor recommendation R-004 is deferred with rationale. No confirmed production correctness defect was found. Coverage includes runtime/contract inspection, targeted test/harness assessment, actual complete tests/builds/installed examples, independent byte-oracle probes, isolated next-version failures, a symlink mutation reproduction and a clean declared-extras backend failure. These are distinct from unavailable native Windows/macOS/Python 3.11/3.14/big-endian execution and from arbitrary corruption/security guarantees not promised by the project.

The user already authorized important corrections, closure and release, so proceed to an ordered revision plan without a new approval pause. Preserve these baseline observations and add recheck/disposition evidence rather than replacing them with later green results.
