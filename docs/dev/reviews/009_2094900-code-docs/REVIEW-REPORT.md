# Comprehensive code and documentation review

## Scope and baseline

Campaign 009_2094900-code-docs; reviewed source 209490063eb2e299243fc7ad99e63a08305e0f3e; working branch revision/009_2094900-code-docs created from main at that exact source. [Review plan](REVIEW-PLAN.md). State: Open, review initialized. No code defect, review completion or executed test is claimed by this opening checkpoint.

## Coverage checkpoints

| Unit | Status | Evidence |
| --- | --- | --- |
| U-001 | Complete | Complete public/facade/source/error/offset/scanner/stream inspection; 197 targeted tests and 3,000 independent scanner cases pass; R-001 reproduced. |
| U-002 | Pending | Formats/backends/producer. |
| U-003 | Pending | Persistence/CLI. |
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
