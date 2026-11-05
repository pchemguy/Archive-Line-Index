# Comprehensive code and documentation review

## Scope and baseline

Campaign 009_2094900-code-docs; reviewed source 209490063eb2e299243fc7ad99e63a08305e0f3e; working branch revision/009_2094900-code-docs created from main at that exact source. [Review plan](REVIEW-PLAN.md). State: Open, review initialized. No code defect, review completion or executed test is claimed by this opening checkpoint.

## Coverage checkpoints

| Unit | Status | Evidence |
| --- | --- | --- |
| U-001 | Complete | Complete public/facade/source/error/offset/scanner/stream inspection; 197 targeted tests and 3,000 independent scanner cases pass; R-001 reproduced. |
| U-002 | Complete | Complete format/adapter/producer inspection; 175 selected checks pass; no additional confirmed finding. |
| U-003 | Complete | Complete filesystem/raw/SQLite/CLI inspection; 150 targeted checks pass; no additional confirmed finding. |
| U-004 | Pending | Packaging/tests/current docs/full checks/consolidation. |

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
