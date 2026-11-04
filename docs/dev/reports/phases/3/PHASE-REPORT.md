# Phase 3 — ZIP and TAR workflows

## Result and selected boundary

T-029–T-040 deliver version 0.3.0 with single-payload ZIP and sequential plain/gzip/bzip2/xz TAR through the existing library/index/persistence/CLI interfaces. The reviewed source is `61c760ac9d4844c317083a693b08e59b333993fa` plus this task's release notes, phase report and HANDOFF. Creation/integration parent is main `e19750c6e79b3c0eb0b135bb9db042a51b6fed70`. This review establishes phase exits; actual merge/tag/release effects remain pending until observed below. Stop before Phase 4/T-041.

## Separate phase code review

Reviewed ZIP/TAR metadata selection, adapter lifecycle and resource ownership together with registry detection, generic stream failure/limit handling, scanner completion, paired-output CLI, persistence and actual installed packaging. Format modules own parsing/codec dependencies; core scanner and persistence are unchanged. Member names never become extraction destinations. Lazy selection preserves the import/runtime boundary. No blocking cross-milestone finding remains.

ZIP validates the full exposed member list before delivery and its member CRC/decompression outcome during exhaustion. TAR streams one member, validates all later exposed entries and strict trailing structure, then drains codec completion before reporting EOF. Ordinary source errors remain ordinary; dependency parsing/extraction failures retain causes. Early close and failed cleanup preserve ownership/retry. Public arrays and stored pairs use original uncompressed payload coordinates.

Milestone findings and rechecks are retained in [3.1](3.1.md) and [3.2](3.2.md). T-029's initial premature mypy claim is superseded by published correction `b3c78bf9363794a3ef71cd59ce3cde24d8ed53ec`; history is preserved and issue closure followed the correction. A source tell() classification defect was reproduced and repaired at the ZIP review. T-036's interrupted edits were recovered intact without rollback. A stale 0.2.0 unit-version assertion was corrected at the TAR review. No unresolved finding is hidden by a passing count.

## Acceptance and phase exits

| Contracts | Actual phase evidence |
| --- | --- |
| ARC-01–03, SYS-01 | ZIP and USTAR/PAX/GNU/plain/gzip/bzip2/xz TAR; every required suffix, signature precedence, unconventional/conflicting names, empty/nested payloads, directories/extension headers and rejection of zero/multiple/metadata/special members and compressed non-TAR candidates. |
| ARC-04–05, API-04, STR-01–05, SYS-04–06 | Real CRC/decompression/footer/truncation failures; late TAR entries, malformed/end-marker/padding rejection, source-I/O category preservation, missing codec/encryption handling, original causes, limits, cleanup/early-close/retry and no false successful terminal EOF. |
| IDX-01–06, API-01–03, SYS-02–03/10 | Original LF/BOM/EOF coordinates, empty content, one-byte/default reads, plain/ZIP/TAR equivalence, exact root exports/import boundaries, borrowed versus owned operation behavior and no completed array on late failure. |
| PER-01–07, CLI-01–06, SYS-07–09/13 | Prior independent canonical SQLite/raw behavior remains covered; single scan and shared array, existing/source-alias protection, default/explicit stems, partial publication, accurate statuses/diagnostics and no archive-failure outputs. |
| API-05, SYS-11–12, release gate | Version 0.3.0 native and source-rebuilt clean installations, all command forms/TAR suffixes, seven README examples, isolated builds, safe stable bundles, native metadata/source equality, full inventory/checksums and the actual naming gate's 38 contract vectors. |

Full suite: 574 tests pass with 96% production statement/branch coverage; ZIP and TAR modules each have 96%. Ruff lint/format over src/tests/scripts and strict mypy over src/scripts pass with --no-native-parser for the known container discovery issue. Native/source-rebuilt installed tests run outside the checkout without development dependencies or source injection. Actual runtime is Linux/CPython 3.12.14; native Windows/macOS/Python 3.11/big-endian execution remains unverified. No CI run or 7z delivery is claimed.

## Persistence, tracking and release preparation

The eleven initial closing commits T-029–T-039 were audited against parent diffs: each has one owning subject, substantive task-owned result/evidence and exactly one initial task checkbox transition. T-029 acceptance/evidence recovery is accounted separately above; no bundled or detached initial checkbox is treated as compliant. T-040 closes with its phase report, notes, HANDOFF and initial task/phase checkoff together; audit its actual result before integration.

Native delivery milestones #10 and #11 are closed with exact issue membership. Issues #38–48 are closed after each source publication/readback; the initial Phase 3 associations were verified before execution. T-040 maps to issue #49 and review milestone #12; close those only after this result is published/read back. T-031's successful push had a timed-out readback, reconciled by a separate exact supervised readback before advancement.

The complete stable hosted inventory is `archive-line-index-wheel.zip`, `archive-line-index-source.zip` and `SHA256SUMS`; valid native wheel/source filenames are internal bundle payloads. Active PLAN/layout/guidance and adjacent reviews reconcile the reloaded naming rule. The actual project gate rejects prior/single-component/Unicode/unknown-extension version notation even with a matching faulty expected list, checks collisions and every staged entry, validates bundled native metadata/contents and checksums. Earlier published tags/assets remain intact. Exact final release artifacts must be rebuilt from the verified default-branch release commit and downloaded after upload for byte identity.

Root RELEASE-NOTES.md contains finalized body-only 0.3.0 notes, including installation/bundle compatibility and actual verification limits. The prior-release baseline is v0.2.0 at `0227494d2e2874f8b09e71cfc49f2c42fc7a3ef8`; complete nonshallow range inspection includes later evidence/plugin/README changes and every Phase 3 task. Curated highlights describe net delivered ZIP/TAR outcomes and packaging changes without repeating previously released plain/persistence capability. No v0.3.0 tag or release exists at this preparation checkpoint.

## Pending integration and release effects

After T-040 publication/readback and issue #49/milestone #12 closure, merge the complete phase into refreshed main with two explicit parents. Verify/publish the merged state, finalize a direct main release commit whose exact body is root RELEASE-NOTES.md, and publish/read back it. Build/check/install the exact source and wheel bundles, execute the complete name/inventory gate before tagging, then publish/read back v0.3.0 at that source. One publisher verifies the complete draft before publication and hosted body/latest/tag/names/downloaded bytes afterward. Retain notes and remove only the owned ignored highlights checkpoint after confirmed body consumption. Record actual identities, URLs, asset sizes/hashes and verification here, publish the outcome/HANDOFF and stop before Phase 4.

Phase preparation recheck: isolated source/wheel build, stable bundle generation and independent complete name/content/checksum validation pass. Fresh installed/integration/documentation/naming checks pass 159 tests against these candidates; the unchanged production boundary retains the full 574-test/96% evidence above. Candidates include the finalized 0.3.0 notes. They are preparation artifacts; exact default-branch source and final hosted-byte evidence remain pending.
