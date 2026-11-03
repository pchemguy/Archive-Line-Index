# Phase 1 — Plain-file library

## Result and reviewed boundary

T-001–T-015 deliver the 0.1.0 plain-file library: owned sequential binary streams, generic borrowed-reader LF/BOM scanning, canonical Q/eight-byte offsets, source-based index building, typed exports, professional executable documentation and native source/wheel verification. This report completes T-015's review; default-branch integration, tag and hosted release remain pending until their actual readback below.

The human's “Finalize Phase 1” instruction supersedes the earlier stop before T-015 and authorizes the phase review, integration and 0.1.0 GitHub release. It does not select Phase 2. Creation/integration parent: main `9c90eebc8aaca66f8f086cb69f93f0dbb7c571ee`; reviewed published source: `15c36f54b49801ee7fe5f2889290ee7f8d4e9593`, plus this task's release notes and source-distribution selection. No runtime code changed during this phase review.

## Code review

Inspected the complete delivered source and cross-milestone interactions separately from testing: source kinds/detection → explicit adapter selection → owned reader/common stream → borrowed scanner/offset model → facade; public exports, exceptions, documentation, packaging and artifact validation. Checked pre-I/O option validation, ownership transfer and constructor failure, bounded/zero/unbounded/readinto behavior, failure/EOF distinction, limit counting before return/copy, closed-state precedence, cleanup notes/retry, prefix/BOM splits, line/sentinel semantics and signed-range enforcement. No blocking findings or contract amendments remain. Prior milestone findings are resolved; retained reports remain scoped evidence rather than substitutes for this phase review.

The complete branch difference is Phase 1 work plus the authorized README overview. The initial 14 task-closing commits were individually audited against their parent diffs: exactly one leading owning ID, actual result paths, evidence and one initial task checkoff together. The separate README maintenance commit is authorized documentation work. T-015 follows the same result/report/checkoff contract. No closed preparation/campaign records are edited.

## Acceptance and exits

| Conditions | Verified Phase 1 evidence |
| --- | --- |
| API-01–05, SYS-10/11 | Exact delivered exports and metadata; validation before acquisition; ordinary filesystem errors; direct/source equality; actual wheel and independently source-rebuilt wheel installed outside checkout without path injection or development tools. |
| STR-01–04 and applicable STR-05/06, SYS-05 | Byte-exact bounded/zero/unbounded/readinto reads, byte capacity/tail preservation, inclusive declared/actual limits, retained delivery failures, no false EOF, explicit/context cleanup and primary-exception preservation. Plain and controlled-reader scope. |
| IDX-01–06, SYS-03/06 | Exact LF/CRLF/lone-CR/empty/unterminated/BOM examples, tiny buffers and legal short reads; invalid results, borrowed ownership, read/overflow/allocation/native-width failures; native block search without complete-line storage. |
| SYS-02/04, ARC-01/02 (applicable portion) | Streaming is independent of indexing; direct scanner uses caller readers; bounded signatures/suffixes select explicit candidates; undelivered archive adapters raise UnsupportedFormatError rather than falling back to plain content. |
| SYS-06 | 32 MiB generated single line and 8 MiB real plain-file delivery retain <128 KiB peak traced working storage with bounded reads; offset storage grows with line count. |
| SYS-11/12 and release preparation | Native wheel/source metadata, source rebuild, required inputs/notices, package-byte equality, safe inventory and checksums; 28 synthetic inventory checks; all three README examples execute against both installed paths. |

These are the phase-applicable portions of the accepted contracts. Persistence/CLI and archive adapter/worker obligations remain assigned to later phases. The full intended public surface is not claimed by 0.1.0. Delivery milestone reports: [1.1](1.1.md), [1.2](1.2.md), [1.3](1.3.md).

## Verification

Linux/bash, CPython 3.12.14. `python -m ruff check src tests scripts`, `python -m ruff format --check src tests scripts`, strict `python -m mypy --no-native-parser`, helper type checking and the full coverage suite pass: 253 tests, 99% combined production coverage. Facade, scanner and common stream are each 100%. Mypy's supported Python parser avoids a container-specific native process-discovery failure; no strict checks are disabled.

`python -m build` succeeds in isolated Hatchling 1.33.0 environments. After adding release notes to the selected source-distribution inputs, six artifact/installed-runtime/example tests pass. Native candidate names are `archive_line_index-0.1.0-py3-none-any.whl` and `archive_line_index-0.1.0.tar.gz`; inventory generation and independent SHA256SUMS readback agree. Native Python filenames retain their required version/tag structure under the accepted PLAN. Final release artifacts must be rebuilt from the exact default-branch release commit, not reused from precompletion candidates.

Native Windows/macOS/Python 3.11 execution is unverified. py7zr is declared and installed but not eagerly imported; archive behavior is not certified in this phase. No CI-run claim is made; checks ran on the available execution host.

## Tracking, notes and pending publication

Readback confirmed delivery milestones #2/#3/#4 closed with 6/3/5 completed issues before T-015. T-015 maps to issue #24, milestone #5 and the verified phase label. After this task commit is published/read back, close #24 then #5 with verified membership. All Phase 2 tasks remain unchecked/unprojected.

Initial-release highlights use complete nonshallow history and complete remote tag/release discovery: no previous tag/release, null baseline. The documentation integration summary establishes accepted preparation, not delivered runtime behavior; the full 38-commit inventory through the reviewed source, all Phase 1 task results/current source and README delta establish the curated user outcomes. Release notes are retained in root RELEASE-NOTES.md; an ignored, untracked highlights checkpoint carries source coverage and stays outside distributions. Incremental integration/release commits must be assessed before publication.

Next: explicitly merge the published phase tip into refreshed main with two parents; verify/publish the merged state; finalize a default-branch release commit with exact notes as its body; rebuild/install/verify its native artifacts; publish/read back v0.1.0 at that exact commit; create one draft, attach source/wheel/SHA256SUMS, verify it and publish. Confirm hosted body, latest pointer, tag target and downloaded bytes. Record actual outcomes here, refresh HANDOFF and stop before Phase 2.

## Integration boundary

T-015 `0fa719b0b08de33cee1124627cf59077230a21a3` is published/read back. Issue #24 and milestone #5 are closed, with one completed member; all delivery milestones were already closed. The complete 15-task persistence audit passes. Phase 1 completion merges that exact source into verified main parent `9c90eebc8aaca66f8f086cb69f93f0dbb7c571ee` using an explicit two-parent merge. No conflicts or unrelated changes are present. The containing merge's publication and later release effects remain subject to readback.

Merged-state verification passes: 253 tests, including native source rebuild and both installed workflows/examples/inventory, plus staged/unstaged diff checks. Runtime source is identical to the reviewed phase tip. Main publication and release preparation follow this merge commit.

Integration `f1365f0457a616917628c8b2a0c8d9bb72b64f14` is published and exact remote main readback matches. Its first parent is the accepted preparation main and second parent is T-015. All Phase 1 issues/milestones are closed. The next direct main commit uses the exact finalized release-note body; tag/package/hosted effects remain pending.
