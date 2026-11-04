# Revision plan

## Campaign and decisions

- Campaign: `001_7c8c72b`; package/branch suffix: `001_7c8c72b-code-review`.
- Original code baseline and branch-off: `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`; original opening commit: `7eedb5efdb5e8ce1a6b8ef333a25c9f36c3fb70c`.
- Revision entry: published review consolidation `227774e18440c61041efcd91adb46be7fff95026`; production/tests/scripts/configuration are unchanged from the original baseline.
- Working branch: `revision/001_7c8c72b-code-review`; creation parent and integration/return target: actual default `main`.
- Sources: [review plan](REVIEW-PLAN.md), [original review and assessment corrections](REVIEW-REPORT.md), [revision report](REVISION-REPORT.md), accepted SPEC and its children, and inspected source/tests/configuration.
- Authority: the human requested “Prepare revision plan, then execute it” after the evidence-based assessment. Prepare/publish the plan, perform its focused repairs and verification, then finish the campaign through verified main integration/publication. No new product scope, version bump or GitHub release is selected; preserve v0.4.0.
- Execution: existing Linux/bash, CPython 3.12.14 with py7zr 1.1.4, pytest 9.2.0 and configured tooling. Prior Windows reviewer execution is attributed evidence, not fresh execution here. Use the existing tool runtime; declared package tests may create their temporary installed-consumer environments. Do not reprovision the tool runtime or claim native Windows/Python 3.14 verification.

| Finding | Selected decision and rationale |
| --- | --- |
| R-007 | Accept the high-priority SQLite fsync repair: use a writable descriptor without truncation. Portable regression enforces the Windows precondition; actual native execution remains a recorded limit. |
| R-001 | Accept explicit inspection I/O control. Raw read-ahead exceeds 512 even with an 8 KiB buffer; it is not solely a Python 3.14 problem. Preserve short-read handling. |
| R-002 | Accept explicit plain buffering as portability/overhead control. Reclassify as a recommendation rather than evidence of unbounded payload storage; the 128 KiB peak threshold is a test expectation, not a normative universal memory cap. |
| R-004 | Accept delivered-byte equality and excess checks within the observable member stream. A count does not detect an undeclared decompressed tail already clipped by zipfile with a matching prefix CRC; do not promise that capability or expand to a new ZIP parser. |
| R-005 | Accept short explicit parameter IDs for portability across allowed pytest versions. Pytest 9.2 defaults already shorten long values; legacy strategy demonstrates the oversized IDs. |
| R-003 | Defer the low-value internal missing-source/missing-required-dependency precedence change. Public detection opens the source first; no redundant stat/open or dependency ownership redesign is selected. |
| R-006 | Treat as an environment evidence gap. Run real py7zr checks in the existing provisioned runtime, retaining actual Windows coverage limits. Preserve >=1.1.4,<1.2; the record's >=1.1.0,<2 is not accepted. |
| R-008 | Reject the pytest-configuration allegation: dev/test extras already declare both plugins, the actual table is [tool.pytest] and asyncio_mode is strict. Accept explicit UTF-8 reads as a separate portability cleanup; do not remove configured plugins/options to accommodate an underprovisioned runtime. |

## Authoritative project updates

No accepted public surface, contract, design, delivery task or layout changes are required. These corrections implement existing requirements; campaign artifacts own the focused actions and evidence. Do not reopen completed TASKS/issues or alter frozen phase/manual records. Current API/module documentation is maintained only where a repair changes its explanation.

## Ordered revisions

| Action | Findings | Outcome and owners | Dependencies | Verification |
| --- | --- | --- | --- | --- |
| V-001 | R-001–R-008 | Reconcile review claims, record selected dispositions and executable plan; preserve original observations as historical evidence. | None | Campaign links, identity, source/config comparisons and document/diff checks. |
| V-002 | R-007 | Synchronize SQLite temporary output through a writable non-truncating handle; retain publication/cleanup semantics. | V-001 | Observe failure with a Windows-like writable-fsync requirement; then SQLite/raw/filesystem/CLI tests and strict types. |
| V-003 | R-001, R-002 | Make detection and plain-reader buffering explicit; enforce the 512-byte detection budget with legal short reads. | V-002 | Failing raw read-ahead and large-default-buffer regressions; green detection/plain/large-input and archive workflows. |
| V-004 | R-004 | Count ZIP bytes delivered and reject observable metadata mismatch at EOF or excess delivery; retain dependency CRC/error behavior. | V-003 | Real overdeclared ZIP fails before fix and rejects afterward; test existing underdeclared CRC rejection, injected excess delivery, retained stream failure and no CLI outputs. Characterize clipped prefix/CRC observability separately. |
| V-005 | R-005 | Assign descriptive short IDs to large TAR/7z payload parameters. | V-004 | Collect under pytest legacy ID strategy and verify portable bounded node IDs; execute all affected cases. No fabricated product RED for test metadata. |
| V-006 | R-008 encoding only | Read project TOML, shared JSON vectors and README text explicitly as UTF-8; retain declared pytest extras/configuration. | V-005 | Observe non-UTF-8-locale TOML/README read failure with a controlled locale boundary; test preserved Unicode metadata/example text and release/example checks. |
| V-007 | All accepted actions; R-006 evidence | Review composition, run full regression/coverage/lint/types and relevant native/source-wheel/package checks, consolidate current dispositions and integrate the verified campaign into refreshed main. | V-002–V-006 | Full results and concrete native limits recorded; maintained links/unwrapped Markdown/closed-record protection; explicit two-parent merge, merged verification and per-commit publication/readback. |

## Execution and persistence

Use one action checkpoint containing its source/test/document changes and observed evidence, followed immediately by supervised publication and exact readback before another action. Retain original observations and append assessment/recheck evidence in this active package only. Action IDs are revision-plan identities, not invented TASKS IDs. Tests precede runtime bug fixes; distinguish observed RED/GREEN, characterization and test-metadata changes. Failed checks retain their actual outcome until repaired and rerun.

## Limits and stopping

Native Windows/macOS/Python 3.11/Python 3.14/big-endian facilities are unavailable here and remain unverified. Portable simulations test named preconditions without certifying those platforms. Complete feasible checks, record limits and deferred R-003, then integrate the verified campaign into its recorded main parent with two explicit parents and publish/read back. Closure freezes this campaign after integration. Stop without a version bump, release, new feature or additional review campaign.
