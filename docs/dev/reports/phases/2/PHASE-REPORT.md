# Phase 2 — Paired persistence and CLI

## Result and reviewed scope

T-016–T-028 deliver version 0.2.0 with independent SQLite/raw persistence and the single-target paired-output command through console, module and importable callable. The existing plain-file streaming/LF/BOM/indexing capability remains covered. All Phase 2 exits, main integration and the published v0.2.0 release are verified below. Phase 3 is not selected.

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

All 13 actual T-016–T-028 closing commits were audited against parent diffs: exactly one owning subject, verified result/evidence and one initial owning checkbox each. T-028 contains its repair/regression, this report, release notes, HANDOFF and initial checkoff together. No earlier closed phase/preparation records are changed. All Phase 2 tracking associations remain verified; issues #25–37 and milestones #6–9 are closed. T-028 maps to issue #37 and final milestone #9.

Packaging recheck: isolated Hatchling 1.33.0 source and wheel-from-source builds pass; native inventory/SHA256SUMS generation and independent verification pass for both candidates. Native filenames retain their ecosystem-required version/tag structure under PLAN; root RELEASE-NOTES.md is included in the source. The final release packages were subsequently rebuilt from the exact default-branch release commit and verified after upload and download, as recorded below.

## Integration and release outcome

The published phase tip is T-028 `15cf302066fa0932e072cb00cdfe406fbdd6a909`. Explicit merge `d4acf064974c7867c713dc01dba94c0180fb4a61` has receiving parent `eaa2dcfdfd756d367c15b9ec4eb763dda2e49c97` and incoming parent `15cf302066fa0932e072cb00cdfe406fbdd6a909`. No conflicts occurred; 399 tests pass on the merged state. Main publication and exact remote readback succeeded. All 13 Phase 2 issues and four milestones are closed.

Direct main release commit `0227494d2e2874f8b09e71cfc49f2c42fc7a3ef8` has the merge as its parent. Its raw body is byte-identical to retained root RELEASE-NOTES.md. The lightweight v0.2.0 tag resolves to that exact release commit locally and remotely; main and tag were separately published and read back. The prior-release baseline is v0.1.0 at `2d0435cc731d608843ad71cfa9c7688d1d8b5d09`; complete range coverage includes the later Phase 1 evidence-only commit and all Phase 2 work without repeating previously released runtime changes.

[Archive Line Index 0.2.0](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.2.0), release ID 432949524, is published stable and confirmed as the repository's latest release. One direct API publisher created/reused the draft, uploaded and verified all three assets before publication, then read back the actual body, tag, state, latest selection and complete asset inventory. No workflow publisher or CI run is claimed. The published body exactly matches the release commit and retained notes. The owned ignored highlights checkpoint was consumed only after this readback; no tracked release notes were removed.

## Final artifact verification

Isolated source and wheel builds use exact release source `0227494d2e2874f8b09e71cfc49f2c42fc7a3ef8`. Packaged source/configuration/README/notes bytes match that Git source. An independent wheel rebuild from the actual source archive passes; native and source-rebuilt wheels have the same observed SHA-256. Both install into clean runtimes outside the checkout and pass public library/persistence workflows, all five README examples, console/module/imported CLI forms, help/usage, real filesystem failure, partial publication and real SIGINT cleanup. No development tools or source-path injection are present in those consumer runtimes. Native filenames retain their version under the project's accepted packaging contract.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| [archive_line_index-0.2.0-py3-none-any.whl](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.2.0/archive_line_index-0.2.0-py3-none-any.whl) | 26232 | `db5cbe9f17304e35b0aad9051c4fc536522a58d5c9a96384f62a62f4a01dcdaf` |
| [archive_line_index-0.2.0.tar.gz](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.2.0/archive_line_index-0.2.0.tar.gz) | 132858 | `363980eac233364bfd65f70d7f0b512c83bdbaa727c2adc2403c466bee7663bd` |
| [SHA256SUMS](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.2.0/SHA256SUMS) | 206 | `1bcc151ccbcf17275769d3bbf9911133655f5ffc5fb170f343306e43e93831e2` |

All three hosted assets were downloaded and their complete bytes verified against the local manifest. Downloaded SHA256SUMS also matches the local checksum file exactly and covers the source and wheel. Artifact inventory, metadata, filenames and checksum readback pass. Runtime verification remains Linux/CPython 3.12.14; no additional native-platform claim is made.

Phase 2 is complete. T-029 and all Phase 3 tasks remain unchecked and unselected. No later-phase tracking or implementation was started. This outcome checkpoint requires its own main publication/readback before the final user report; the release tag remains pinned to the release source above.
