# Phase 3 — ZIP and TAR workflows

## Result and selected boundary

T-029–T-040 deliver version 0.3.0 with single-payload ZIP and sequential plain/gzip/bzip2/xz TAR through the existing library/index/persistence/CLI interfaces. The reviewed source is `61c760ac9d4844c317083a693b08e59b333993fa` plus this task's release notes, phase report and HANDOFF. Creation/integration parent is main `e19750c6e79b3c0eb0b135bb9db042a51b6fed70`. All Phase 3 exits, main integration and the published v0.3.0 release are verified in the final outcome below. Stop before Phase 4/T-041.

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

## Integration boundary

T-040 `04b665b4121847e91b8911673cdd50e0768b043a` is published/read back. All 12 Phase 3 issues #38–49 and native milestones #10–12 are closed. The final parent-diff audit confirms all 12 initial single-task closing compositions, with T-029 acceptance recovery separately retained. Frozen prior-phase/manual/plugin records are unchanged. The complete phase is merging into refreshed creation parent/default main with receiving tip `e19750c6e79b3c0eb0b135bb9db042a51b6fed70` and incoming tip `04b665b4121847e91b8911673cdd50e0768b043a`. No conflicts occurred. Actual merged-state verification/publication and exact-source release effects remain to be observed.

Prospective merged-state verification passes all 574 tests, including actual installed native/source-rebuilt artifacts, all supported archive workflows and release-bundle checks. Product source matches the reviewed phase tip. The explicit merge commit and its publication require subsequent observation.

Integration `bc8d64edcb9494ed3ac9da711a69ae3963ab6e1a` is published and exact remote main readback matches. Its two pinned parents and all 574 merged-state tests are verified. The next direct main release commit finalizes the already prepared notes/body; its exact source/bundle/tag/hosted outcomes remain pending. All 12 Phase 3 issues and three milestones are closed.

## Final integration and release outcome

The complete phase is integrated and published on main as `bc8d64edcb9494ed3ac9da711a69ae3963ab6e1a`, with receiving parent `e19750c6e79b3c0eb0b135bb9db042a51b6fed70` and incoming T-040 tip `04b665b4121847e91b8911673cdd50e0768b043a`. All 574 merged-state tests pass; exact remote main containment/readback is verified. All 12 issues #38–49 and milestones #10–12 are closed. No Phase 4 task or tracking projection was started.

Direct main release commit `2490b645891be7ae0ab7763d1aa7fe195b730b83` has the integration merge as its parent. Its raw body is byte-identical to retained root RELEASE-NOTES.md. Lightweight tag v0.3.0 resolves to that exact source locally and remotely, separately published/read back before the single protected release publisher ran.

[Archive Line Index 0.3.0](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.3.0), release ID 433481126, is published stable and confirmed as the repository's latest release. The publisher validated the local full inventory before each stage, created/reused one draft, uploaded only missing matching assets, verified all three draft assets before publication and read back actual notes/tag/state/latest/names/digests. The actual naming gate ran against complete draft and hosted inventories. No CI publisher/run is claimed.

## Exact-source artifacts and downloads

Isolated native source/wheel builds use exact release source `2490b645891be7ae0ab7763d1aa7fe195b730b83`. The full complete-inventory name/content/checksum gate passes before tagging/publication. Both stable bundles contain exactly their safe native package with matching metadata. All 107 packaged tracked source/configuration/test/script/document bytes were compared against that Git source. An independent wheel rebuild from the actual bundled source distribution passes; native and source-rebuilt wheels have the same observed SHA-256, `6e8d022623cbca5269539213eaf2c4ffcf208bd54ce0a12dbd99ee72f592eb3b`.

Both actual bundle-derived variants install into clean runtimes outside the checkout and pass public library/persistence workflows, seven executable README examples, six plain CLI cases and 31 ZIP/TAR cases per variant. These include console/module/imported forms, every required TAR suffix, empty and late-invalid payloads, corruption, partial publication and real SIGINT cleanup. Installed runtimes contain no development tools or source-path injection. Runtime dependency py7zr is 1.1.4; no 7z adapter suitability/delivery is inferred from its presence.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| [archive-line-index-source.zip](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.3.0/archive-line-index-source.zip) | 154864 | `0f1c8723eab93dd2b3302f9e9742c565c3b49d20ed03a1ba0b7374709849e52e` |
| [archive-line-index-wheel.zip](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.3.0/archive-line-index-wheel.zip) | 32350 | `a420070c537fae2ea3a9bfca40e87a86d2477e245c2a89584860fec70182b1c6` |
| [SHA256SUMS](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.3.0/SHA256SUMS) | 191 | `55e646d2d74c37cf6690efc03d034bfb3352bdb91a994c524d58adf078d8945a` |

All three tag-specific assets were downloaded and their complete bytes matched the local manifest. Downloaded SHA256SUMS exactly matches the local file and covers both bundles. Every advertised latest/download URL was also fetched and its bytes matched the same hashes. Stable filenames, source association, body, latest selection and hosted integrity are verified independently of a successful upload response.

The full release history coverage is pinned to prior v0.2.0 through the exact release source. The published body exactly matches finalized notes with no checkpoint front matter. Root RELEASE-NOTES.md is retained. Only the owned ignored highlights checkpoint was removed after confirmed published-body consumption. Runtime verification remains Linux/CPython 3.12.14; other native platforms remain unverified.

Phase 3 is complete. This containing documentation outcome commit requires its own main publication/readback before the final user report. The release tag stays pinned to the exact release source above; T-041 and all Phase 4 tasks remain unchecked and unselected.
