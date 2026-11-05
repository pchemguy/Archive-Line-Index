# Comprehensive code and documentation review

## Scope and baseline

Campaign 009_2094900-code-docs; reviewed source 209490063eb2e299243fc7ad99e63a08305e0f3e; working branch revision/009_2094900-code-docs created from main at that exact source. [Review plan](REVIEW-PLAN.md). State: comprehensive review complete; campaign Open for decisions. Three confirmed findings remain Open. The opening checkpoint originally initialized the review; subsequent units and actual checks are recorded below.

## Coverage checkpoints

| Unit | Status | Evidence |
| --- | --- | --- |
| U-001 | Complete | Complete public/facade/source/error/offset/scanner/stream inspection; 197 targeted tests and 3,000 independent scanner cases pass; R-001 reproduced. |
| U-002 | Complete | Complete format/adapter/producer inspection; 175 selected checks pass; no additional confirmed finding. |
| U-003 | Complete | Complete filesystem/raw/SQLite/CLI inspection; 150 targeted checks pass; no additional confirmed finding. |
| U-004 | Complete | All 77 Python module inventories/current docs assessed, scripts/fixtures reviewed, full suite/build/tools pass; R-002/R-003 confirmed. |

## U-001 — Public API, offsets, scanning and stream lifecycle

Inspected package exports and executable wrapper, api.py, sources.py, errors.py, offsets.py, scanner.py and stream.py completely, with PROJECT/ARCHITECTURE/DECOMPOSITION and public API, line-index, stream and progress contracts. Reviewed corresponding validation/ownership/failure tests, including stream retained-error and cleanup-retry cases. Public construction uses automatic backend selection internally; the scanner remains borrowed-reader-only and persistence is independent. Validation priorities, LF/BOM/sentinel rules, size limits and progress snapshot/cadence match the inspected contracts. No partial index or apparent EOF-after-failure defect was found in these paths.

Executed 197 targeted API/source/offset/scanner/stream/progress/export tests: all passed in 0.36 seconds. An independent simple LF-offset oracle passed 3,000 deterministic generated payload/BOM/buffer combinations. Probes used the current source through command-local PYTHONPATH=src; no product file was edited. An initial standalone probe omitted that path and failed to import the package, then was corrected; that setup failure is not a product finding.

### R-001 — Successful close retains failed-read payload buffers

- Priority/type/status: Moderate resource-lifecycle defect; Open. Confidence: high, reproduced.
- Location: src/archive_line_index/stream.py:50–55 stores the exception; :97–105 accumulates unbounded-read blocks and retains its failure traceback; :168–173 closes the reader but never drops _failure. Related obligation: spec/content-stream.md, State and failure priority and Close and producer outcomes, require failure retention until explicit closure and successful close to release package-owned buffers.
- Evidence: a controlled reader yielded twenty distinct 1-MiB blocks then raised OSError. After read() failed, exception handling exited, stream.close() succeeded, reader.closed and stream.closed were True, and garbage collection ran. tracemalloc still reported 20,974,196 live bytes; dropping the closed stream reduced live bytes to 737 (20,973,459 released). The stream's retained exception traceback keeps the read frame and its blocks list alive. No external exception reference was retained by the probe.
- Impact: a caller retaining a closed stream after a late failure can retain the full accumulated unbounded payload, potentially very large. This does not show a bounded-read whole-payload materialization bug; the failure is resource retention after explicit successful close. Existing tests assert handles/closed state but do not expose this memory lifetime.
- Proposed correction: release the stream's retained failure reference after resource closure succeeds, while preserving retained-error behavior before close, cleanup-retry state if close fails, and externally raised exception objects/notes. Do not mutate an exception owned by the caller merely to erase traceback evidence.
- Objective recheck: retain the closed stream but discard the caught exception, prove accumulated/read-frame resources become reclaimable after successful close, and rerun retained-error, read/readinto priority, cleanup-retry and late-failure tests. No repair is authorized by this review.

## U-002 — Format detection, adapters and producer bridge

Inspected formats.py and every backend owner: package marker, base protocol/size validation, plain, registry, ZIP, TAR, producer and sevenzip. Compared against archive handling and internal API/lifecycle contracts plus README format and memory/cancellation guidance. Reviewed format tests, all backend test scenario inventories and consequential ZIP-size, TAR trailing/footer, producer startup/join/cancel and actual 7z backpressure/CRC cases and fixture generators.

Confirmed bounded signature inspection and signature-before-suffix selection, no malformed-archive plain fallback, sole regular-member policy without path extraction, ordinary source-I/O error preservation, and format-specific EOF validation. TAR's strict end-marker/trailing scan and compressed-reader drain cover late invalid data; ZIP deliberately claims observable member-stream validation rather than extra corruption detection unavailable through its dependency. 7z metadata precedes delivery; the worker owns extraction cleanup, queue cancellation is independent of capacity, transport is finite and close joins rather than abandoning the thread. The documented cooperative cancellation/dependency-memory limitations remain necessary and are not defects merely because shutdown has no absolute deadline. _QueueReader does clear its retained error on successful close; R-001 belongs to the common stream layer.

Executed 175 selected format/backend/full-format lifecycle/backpressure tests, all passed in 4.65 seconds. Checks include actual required TAR filters and 7z codecs, independent instances, exact limits, full-queue early close, producer outcomes, CRC/truncation and SIGINT cleanup. No additional confirmed bug or documentation conflict is recorded for this unit. This is bounded inspection/execution evidence, not proof of safety for every archive or native platform.

## U-003 — Persistence publication and CLI configuration

Inspected persistence package marker, fs.py, raw.py, sqlite.py and cli.py completely against public API/persistence/CLI/progress contracts and README outputs/workflows. Examined test coverage for short/zero raw writes, opposite-endian conversion, exact schema and ordered loads, sidecars/WAL, protected destination races, pre/post-publication cleanup failures, source aliases, one-scan writer ordering, parser errors/statuses, existing application logging and repeated invocation restoration. No broad exception conversion was inferred to be correct without checking where ordinary source/filesystem errors are preserved.

Protected creation uses exclusive linking rather than a racy existence-check/rename; overwrite replaces a completed sibling. Raw and SQLite preserve canonical values and independently publish; the CLI truthfully reports already completed publications and does not claim a two-file transaction. SQLite readers use encoded read-only URIs and strict canonical schema checks; raw conversion borrows and does not mutate input. The CLI configures the emitting scanner logger inside a restoration context and respects effective application handlers, propagation and caller serialization. No additional confirmed functional or contract defect was found in this unit.

Executed 150 targeted persistence/CLI/publication/equivalence cases, all passed in 0.97 seconds. An initial ad-hoc test command cleared configured addopts, thereby disabling the repository's deliberate importlib mode and producing a duplicate test_cli module collection mismatch. Re-running with --import-mode=importlib restored the configured import behavior and passed; this was review-runner setup, not an unresolved project collection defect. Full configured test invocation remains part of U-004.

## U-004 — Packaging, test infrastructure and current documentation

Inspected all three packaging/checker implementations and script/package markers, pyproject tooling/build selection, root/integration conftest, fixture/read/installed-package/archive helpers, installed CLI/runtime/example/archive tests and synthetic release validation/name-vector tests. Inventoried all 77 project-owned Python modules: 22 production, four scripts and 51 test/support modules (243 named test functions before parametrization). Every module has a module docstring. Production/script owners were read as complete implementations; test review combines every module's purpose/scenario inventory with detailed inspection of consequential assertion/fixture bodies, not an independent proof of every test assertion. Google-style public documentation, ownership, errors, import boundaries and declared examples were compared with the inspected interfaces; no additional API-surface discrepancy was confirmed.

Current documentation coverage includes complete README and consumer links, AGENTS/project instructions, SDD/disclosure notices, PROJECT/ARCHITECTURE/DECOMPOSITION, public/internal API declarations, SPEC and its seven contracts, delivery PLAN, layout root/three children, and current task identity/navigation. Current product/code/doc bytes remain identical to the campaign baseline; only this campaign's records and HANDOFF changed. Closed preparation/QC/campaign/feature/phase reports and manual transcripts were excluded from current-validity inspection; their linked existence can be checked without reading their contents. Vendored SDD plugin is external tooling, not reviewed product implementation.

Artifact checkers reject unsafe/special/duplicate entries, forbidden development/credential/cache material, native identity/package-byte mismatches, checksum faults and prohibited outer names. Installed checks independently rebuild from source and exercise clean runtimes rather than importing through the checkout. This does not certify arbitrary supplied archives or every possible artifact mutation; tools operate on project build candidates. Test collection intentionally depends on configured importlib mode and explicit checkout/src pythonpaths, while installed consumers remove those injections.

### R-002 — Current test ownership map points to undelivered filenames

- Priority/type/status: Minor documentation/navigation drift; Open. Confidence: high.
- Location: docs/dev/layout/tests.md:28–29 lists test_index_building.py and test_resource_lifecycle.py under tests/integration; neither file exists. Actual relevant delivered owners include test_full_format_lifecycle.py, test_zip_workflows.py, test_tar_workflows.py, test_sevenzip_stream.py, test_sevenzip_index_cli.py and test_sevenzip_backpressure.py. The map still uses initial allocation placeholders despite completed delivery.
- Consequence: people/agents using the physical ownership map are directed to nonexistent files and cannot reliably locate the implemented source-index/lifecycle checks. The map's general intended-allocation disclaimer explains its origin but does not reconcile the delivered ownership. Existing executable tests do cover these capabilities; this is not a finding of missing test functionality.
- Proposed amendment/owner: reconcile the current layout test map with actual cohesive test owners and distinguish any truly future allocation explicitly. Do not create empty tests merely to satisfy old names. This is a current layout-document amendment requiring acceptance; leave prior closed reports unchanged.
- Objective recheck: every listed concrete delivered test path resolves, actual principal workflow/lifecycle owners are discoverable, and no coverage assertion is inferred solely from filenames.

### R-003 — Markdown formatter defaults contradict the no-wrap policy

- Priority/type/status: Moderate tooling/documentation-policy conflict; Open. Confidence: high, reproduced.
- Location: pyproject.toml:183–189 sets tool.flowmark.width = 88 and semantic = false; AGENTS.md:62 directs Flowmark use but explicitly prohibits hard-wrapping Markdown unless requested. The user's standing instruction likewise requires single-source-line paragraphs/list items.
- Evidence: passed the same single 677-character Markdown paragraph to the installed flowmark console entry via stdin, output to stdout, without writing a file. Default project configuration produced eight nonempty lines (maximum width 86); --width 0 produced one nonempty 677-character line. Installed CLI help explicitly documents width 0 as disabling wrapping. semantic=false alone does not prevent width-based wrapping. An initial python -m flowmark probe found no __main__; using the package's installed console entry is the supported command and gave the reproduction.
- Consequence: a routine formatter invocation following the configured tool defaults can systematically violate the required Markdown source style, especially across broad documentation updates. No repository Markdown was reformatted by this probe.
- Proposed correction: align project Flowmark defaults with the accepted no-wrap policy (width 0, retaining disabled semantic breaks), and document a scoped/check-only invocation if needed. Do not reformat closed histories or perform an unrelated whole-tree cleanup.
- Objective recheck: the project-default formatter preserves one-line long paragraphs and list items without an ad-hoc width override, maintains required Markdown structure, and scoped checks leave protected artifacts untouched.

## Verification results

| Check | Actual result |
| --- | --- |
| Configured full suite: python -m pytest --cov=archive_line_index --cov-report=term-missing | 755 passed in 54.76 seconds; 95% production statement/branch coverage. No skips or warnings reported. Stream module coverage is 100%, but the separate R-001 memory-lifetime reproduction still fails its intended closure guarantee. |
| Ruff lint and formatting across src/tests/scripts | Passed; 77 files already formatted. |
| Strict mypy --no-native-parser src scripts | Passed; 26 source/script files. The supported parser workaround is documented; no native-parser success is claimed. |
| Independent scanner oracle | 3,000 generated byte/BOM/buffer cases matched hand-derived LF/sentinel rules. |
| Focused U-001/U-002/U-003 runs | 197 / 175 / 150 checks passed, respectively; do not add these overlapping counts to the full-suite total. |
| Fresh python -m build --no-isolation | Native 0.5.0 wheel and sdist built successfully from the review worktree. Product bytes match the baseline; source package also includes current review records, so this is a local candidate, not a new exact-tag release. |
| Bundle production and independent --check | Stable wheel/source ZIPs and SHA256SUMS passed native metadata/package equality, bundle content and checksum checks. |
| Separate complete artifact-name gate | Passed all three actual outer names; shared bad-name vectors also ran in the full suite. |
| Current maintained document paths | All local path links resolved across 24 selected current root/design/spec/layout documents. References to closed records were checked only for existence. Full external URL/remote CI/hosted download verification was not performed. |
| Structural/doc coverage | 77 module docstrings present; all test modules inventoried; current interface/contract examples assessed. Source presence alone is not proof of adequate documentation or test semantics. |
| R-001 / R-003 controlled fault/policy probes | Confirmed memory retention after successful close and default formatter wrapping, respectively; no source/config/doc repair made. |

Build/check outputs were kept outside the repository: ali-009-native, ali-009-bundles and transient command logs. These are reproducible review evidence, not release artifacts offered for publication. No tag, release, hosted asset, settings, product code or test was changed.

## Consolidated findings and readiness

| Finding | Priority | Status | Recommended next action |
| --- | --- | --- | --- |
| R-001 | Moderate | Open | Repair successful-close failure-reference lifetime with targeted memory/state regressions. |
| R-002 | Minor | Open | Reconcile the current test ownership map with delivered files. |
| R-003 | Moderate | Open | Align Flowmark defaults with the explicit no-hard-wrap policy and verify nonmutating examples. |

The review found one confirmed runtime resource-retention defect, one documentation navigation issue and one formatter/policy conflict. No Critical issue was confirmed within this coverage. The package builds and its configured suite passes; that does not close the reproduced defect or authorize release-readiness claims beyond these checks. Recommended revision priority is R-001, then the independent R-003 configuration correction and R-002 current-document map update, with test/doc checks matched to their changes.

All review units are complete and this report is the selected stopping deliverable. The campaign remains Open for human decisions. No fixes, revision plan execution, closure, integration, version bump or release are authorized by the review request. Actual host is Linux/CPython 3.12.14 with py7zr 1.1.4; native Windows/macOS, other Python versions, physical big-endian execution, remote CI and current hosted bytes remain unverified. The earlier observed setup failures were corrected as described and are not unresolved product test failures. Review publication/readback is still required for this containing final checkpoint.
