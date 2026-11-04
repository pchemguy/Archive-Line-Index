# Phase 5 — Lightweight progress logging

Feature 006_c33ec54-progress-logging; original branch-off c33ec544e06134ab71866a4bf2f46ad21c9d150d; original opening 2273ec25cd9c9428dc038fb759b1c0db1e51df21. Preparation 368f3b1e7afdc902f91395f0aa1106cf78d7767b is published on main with all nine FDOCS issues and milestone #16 closed. Implementation branch feature/006_c33ec54-progress-logging returns to creation parent main. Human accepted FEATURE and preapproved autodoc, whole-package QC and full T-053–T-056 delivery; retained per-phase release policy selects version 0.5.0.

## Delivered behavior and acceptance

Scanner-owned archive_line_index.scanner emits cumulative original/uncompressed-byte INFO progress at chunk boundaries, with at least five seconds between periodic records and an exact final count after EOF/offset validation. No line-level work or disabled clock/record work is added. Library configuration remains caller-owned. CLI --log-level defaults INFO, reuses effective application handlers or owns one temporary stderr handler, and restores the emitting logger's prior level without changing root/parent/handler/propagation/disabled state. WARNING suppresses even a previously INFO child. Stdout/status/index/resource/publication behavior is unchanged; scan completion is not publication success.

| Conditions | Actual evidence |
| --- | --- |
| LOG-01 | Exact empty/BOM/short-reader totals and unchanged offsets; actual plain/ZIP/TAR/gzip/bzip2/xz/7z payload counts, independent stored-pair checks. |
| LOG-02 | Controlled 4.999/5.0/large-jump clocks, no catch-up burst, independent timers and exact final values. |
| LOG-03 | Forbidden clock/INFO calls when disabled, constant observation cost across equal-sized dense/sparse LF inputs, retained bounded-read/scanner tests. |
| LOG-04 | Source/memory/interruption/array-validation failures lack completion; actual corrupt ZIP/TAR/7z probes reject and emit no scan-complete. Existing cleanup/worker/CLI failure regressions remain green. |
| LOG-05 | All installed console/module/imported paths pass default progress, case-insensitive warning suppression, invalid usage, output/status/persistence/protection and partial-failure behavior. |
| LOG-06 | Existing root/effective/custom handlers and formatter identity, explicit child level, disabled/NullHandler behavior, repeated calls, setup/scan exceptions and restoration are exercised by tests and fresh-review probes. |
| LOG-07 | README configuration/suppression/cadence semantics; eight complete examples run against native/source-rebuilt installations; current main docs and exact package inventories align at 0.5.0. |

## Fresh review and disposition

A fresh-context read-only reviewer assessed implemented HEAD 8e9b85e8e393f97d1566f69a49bc07f204cf5c27 plus the then-current main-document incorporation against accepted feature contracts and failure/cost/configuration focus. Verdict: Ready to merge; no Critical or Important finding and no production defect. The author's separate milestone review is in 5.1.md; passing tests are not substituted for either code assessment.

- M-001 (Minor, deferred): tests/integration/test_installed_archives.py's corrupt ZIP/TAR/7z cases require errors but do not permanently assert absence of Scan complete. A regression could escape those particular assertions; current implementation is correct and the independent three-format phase probe confirms rejection without completion. Future bounded test hardening can add those assertions.
- M-002 (Minor, deferred): the installed progress test snapshots root state after its first package import. It tests CLI-module import/configuration but not that first import directly. Fresh clean-interpreter/package-root probes confirm current imports leave logging unchanged; move the snapshot earlier in a later test-hardening change.

No production correction was required after fresh review; minors remain explicitly deferred rather than labeled fixed. The following reviewed boundaries were consciously excluded and reconciled against accepted scope: unavailable native Windows/macOS/other Python/big-endian execution remains unverified; shared CLI/logging reconfiguration is caller-serialized; custom handler costs/failures use standard application logging semantics; standalone stream/per-row persistence, progress bar/ETA/throughput/compressed counters/callbacks/heartbeat are accepted non-goals. Prior closed campaigns/manual records are protected history. T-056 transfer/archive/report and actual release publication remain this workflow's responsibilities, not waived by review. No new scope ruling or missing human decision is inferred from these existing boundaries.

## Verification and source disposition

Observed T-053/T-054 RED/GREEN and pytest 9.2 capture-fixture sensitivity are retained in task/milestone evidence. Final full post-incorporation/archive tree pytest with coverage passes 755 tests in 34.24 seconds at 95% production statement/branch coverage, with no reported warning/skip. Ruff lint/format pass over 77 files; strict src/scripts mypy passes over 26 files using --no-native-parser. Current maintained links, 56 distinct acceptance IDs, unique canonical 56-task IDs and dependency/checkbox composition pass. Actual host Linux/CPython 3.12.14, py7zr 1.1.4; no native target certification is implied.

Actual pending-tree 0.5.0 wheel/source and stable source/wheel ZIP candidates pass native/source equality, metadata/tag agreement, complete content/checksum checks and the independent version-free three-asset naming gate; shared name-notation vectors run in the full suite. Those are phase candidates, not tagged release bytes. Final report/task/status additions and the receiving main/release boundary require an exact committed-source rebuild and installed/hosted byte verification before release completion.

Main PROJECT/architecture/decomposition/API/SPEC/progress/CLI/PLAN/layout own the resulting system and affected conformance rechecks. Main TASKS receives completed T-053–T-056 with stable scope/dependencies; the archived FEATURE-TASKS is explicitly historical and no active second owner remains. All feature preparation sources, their QC reports and task/control evidence are retained together in this campaign directory with valid in-scope links. Root guidance commands/authorities remain current, so AGENTS does not need an unrelated rewrite. All prior closed campaign/phase/manual/preparation records remain unchanged.

## Task persistence and pending integration

T-053 c11121153017b5c70d5f02e0c2bcc2e77359f3df, T-054 a28a041910d68c71faf82ff1f6a5ca08fa003174 and T-055 8e9b85e8e393f97d1566f69a49bc07f204cf5c27 each have exactly one initial owning task checkbox, a single leading T-ID subject and coherent source/tests/result evidence, with publication/readback and issue closure. Delivery milestone #17 is verified closed. Their new main-list checkboxes are accepted transfers, not additional completions. This containing T-056 checkpoint introduces only T-056's initial completion while transferring the finished list, archive, reports and continuity coherently.

Publish/read back T-056, close/read back issue #75 and milestone #18, explicitly merge the complete verified feature into refreshed main, verify/publish it and freeze this campaign. Then create the direct-main 0.5.0 release commit with exact finalized notes, rebuild/check/install its source and wheel, pass actual naming/inventory gates, publish/read back the pinned tag and single GitHub release, and verify hosted body/assets/latest/downloaded bytes. These external effects are pending until actually observed; final Git integration messages and current HANDOFF retain their exact facts. Do not move tags or amend this frozen phase report afterward merely to add release history.
