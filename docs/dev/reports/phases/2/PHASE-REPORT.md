# Phase 2 — Paired persistence and CLI

## Result and reviewed scope

T-016–T-028 deliver version 0.2.0 with independent SQLite/raw persistence and the single-target paired-output command through console, module and importable callable. The existing plain-file streaming/LF/BOM/indexing capability remains covered. This review establishes Phase 2 exits; integration/tag/hosted release remain pending actual readback below. Phase 3 is not selected.

Reviewed published source `08f251e75cfd44bc3bd82aad4679b234e4c41e57` plus this task's WAL reader correction, regression and refreshed release notes. Creation/integration parent is main `eaa2dcfdfd756d367c15b9ec4eb763dda2e49c97`. The complete branch difference fits the selected phase; accepted design/contracts/PLAN/layout remain unchanged. Reviewed fs/raw/sqlite, facade/shared offsets, public exports, CLI/runner, packaging and README as one capability separately from test execution. No blocking findings remain.

## Review findings and recovery

Finding R1: forcing SQLite immutable mode ignored a committed WAL value and returned `[0]` instead of `[0, 9]`. The new regression failed before correction. Ordinary mode=ro now observes committed database values while the regression confirms unchanged main/WAL data; package writers still publish self-contained DELETE-journal files. This uses the existing read-only SQLite contract, not a new product interface. Reference: SQLite [URI](https://www.sqlite.org/uri.html) and [WAL](https://www.sqlite.org/wal.html) documentation.

The execution environment disconnected during final packaging. All three uncommitted owned files were recovered intact; no rollback, duplicated task result or partial completion commit was created. [Issue #37 recovery note](https://github.com/pchemguy/Archive-Line-Index/issues/37#issuecomment-6608725778) preserved the repair/regression/draft. After access returned, publication, milestone/tag state, source checks, full tests, task composition and packaging were rechecked rather than assuming lost operations succeeded. Earlier milestone schema-prefix and parser resource-status findings remain resolved and covered.

## Acceptance and phase exits

| Conditions | Actual Phase 2 evidence |
| --- | --- |
| PER-01/02/07, SYS-07 | Exact original/SQLite/raw equivalence including empty/BOM-only/EOF arrays, dedicated INTEGER PRIMARY KEY rowid table, headerless little-endian bytes, newly owned reader arrays, simulated opposite-endian conversion without caller mutation and persistence without payload paths. |
| PER-03–05, SYS-08 | Validation before allocation, protected existing/dangling/commit-time names, safe unsupported exclusivity, explicit atomic whole-file replacement, flush/close/publication failures, retained primary/cleanup notes and accurate post-publication destination state. |
| PER-06, SYS-09 | Read-only schema/integrity/value validation, extra/changed objects and rowid/type rejection, corrupt/partial raw/SQLite inputs, canonical range/order enforcement, ordinary filesystem versus engine/corruption categories and committed WAL visibility. |
| CLI-01/02/04, SYS-13 | One scan and the same array to SQLite then raw; input-directory/final-suffix/dotfile/space/hyphen stems, explicit shared stem, both-path protection and lexical/hard/symlink source aliases even with overwrite. |
| CLI-03/05/06 | Help/usage 0/2 without input/output I/O or SystemExit; expected failure 1/interruption 130; no success summary on failure; known completed paths/notes retained; imports do no command work; actual clean installed console/module/imported forms. |
| API-01–05, SYS-10/11 | Exact delivered exports/signatures, validation/ownership/error behavior, 0.2.0 metadata and console entry, native source/wheel plus independent source rebuild and no development tools/PYTHONPATH injection in installed runtimes. |
| SYS-02–06/12 | Phase 1 streaming/index regressions remain green, including bounded long-line storage, LF/BOM/short-read/error/cleanup cases. Five README Python examples execute on both installed variants; native limits and later archive obligations remain explicit. |

Milestone evidence: [2.1](2.1.md), [2.2](2.2.md), [2.3](2.3.md). No two-file transaction, archive adapter, batch mode or additional CLI options are claimed. Library functions retain ordinary raising behavior; only CLI orchestration prints diagnostics/returns statuses.

## Verification and persistence

Restored host: Linux/bash, CPython 3.12.14. Ruff lint/format, strict mypy with the supported --no-native-parser workaround and helper type checking pass. The full suite passes 399 tests with 96% combined production coverage; CLI/module runner are 100%. It includes native/source-rebuilt clean installed workflows, all three commands, five executable README examples and real SIGINT/raw cleanup. Native Windows/macOS/Python 3.11/big-endian execution remains unverified. No CI-run claim is made.

The 12 actual T-016–T-027 closing commits were audited against parent diffs: exactly one owning subject, verified result/evidence and one initial owning checkbox each. T-028 closes with its repair/regression, this report, release notes, HANDOFF and initial checkoff together. No earlier closed phase/preparation records are changed. All initial Phase 2 tracking associations remain verified; delivery milestones #6/#7/#8 are closed. T-028 maps to issue #37 and final milestone #9.

Packaging recheck: isolated Hatchling 1.33.0 source and wheel-from-source builds pass; native inventory/SHA256SUMS generation and independent verification pass for both candidates. Native filenames retain their ecosystem-required version/tag structure under PLAN; root RELEASE-NOTES.md is included in the source. Exact final release packages must be rebuilt from the default-branch release commit after integration, then uploaded and downloaded for byte identity.

## Integration and release handoff

After this result is published/read back, close #37 then milestone #9 with its verified sole member. Explicitly merge the published phase tip into refreshed main with two parents; verify/publish the merged state. Finalize a direct main release commit whose exact body is RELEASE-NOTES.md, publish/read back it, rebuild/check/install its exact native artifacts, and publish/read back v0.2.0. Use one draft publisher; verify all assets before publication and actual notes/latest/tag/downloaded bytes afterward.

The previous-release baseline is verified v0.1.0 at `2d0435cc731d608843ad71cfa9c7688d1d8b5d09`; complete history and remote tag discovery show no pending v0.2.0 release/tag. Curated changes cover its later Phase 1 evidence-only commit and all Phase 2 work without repeating already released outcomes. Refresh the ignored highlights checkpoint through the final release source, retain RELEASE-NOTES.md and consume only the owned draft after body readback. Record actual merge/release identities and hashes here, then stop before T-029/Phase 3.

## Integration boundary

T-028 `15cf302066fa0932e072cb00cdfe406fbdd6a909` is published/read back. Issue #37 and milestone #9 are closed; all 13 task issues and four milestones are complete. Every initial closing commit passed the bounded parent-diff audit. The complete phase integrates into creation parent/default main with receiving parent `eaa2dcfdfd756d367c15b9ec4eb763dda2e49c97` and incoming tip `15cf302066fa0932e072cb00cdfe406fbdd6a909`. No conflicts or unrelated changes are present. Merged-state verification/publication and release effects are recorded after observation.

Prospective merged-state verification passes: 399 tests including native/source-rebuilt installed commands, persistence, executable examples and artifact inventory. Runtime source matches the reviewed phase tip. Diff checks pass; main publication remains pending this merge commit.

Integration `d4acf064974c7867c713dc01dba94c0180fb4a61` is published and exact main readback matches. The next direct main commit finalizes the release body/source; native package/tag/hosted outcomes remain pending. All 13 Phase 2 issues and four milestones are closed.
