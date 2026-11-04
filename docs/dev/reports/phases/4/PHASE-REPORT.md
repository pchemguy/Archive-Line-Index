# Phase 4 — 7z and complete-system delivery

## Result and separate phase review

T-041–T-052 complete the accepted implementation with actual single-payload 7z streaming/indexing and all-format library/SQLite/raw/CLI workflows. Reviewed source through `b5e850e25885bb48db0aef9689d748a5f77a18c9`; this containing T-052 commit adds final reports, notes and initial task/phase completion. Branch `phase/4-sevenzip-completion` was created from main `d1d233a179cb249ddff3cc510ad89974d0ca53c2`. The human authorized all remaining tasks, full verification, integration and v0.4.0 release, then stop.

Reviewed the complete adapter/producer/registry/common-stream/facade/scanner/persistence/CLI interaction separately from test execution, using accepted contracts and actual installed dependency source. One non-daemon 7z worker forwards bounded immutable blocks with independent cancellation/terminal outcomes. Metadata validation precedes startup; producer success follows extraction, callback size agreement and owner cleanup. FIFO data may precede failure on bounded reads, but validated EOF/completed arrays and CLI publication cannot precede terminal success. No filesystem member extraction or whole-payload bridge exists.

Reviewed source-I/O identity, dependency parsing/codec causes, allocation/startup failures, primary-versus-cleanup errors, failed join/archive-close retry, actual SIGINT, full-queue cancellation and simultaneous independent instances. Generic scanner/persistence remain independently usable; the CLI scans once and publishes SQLite then raw with accurate partial-output diagnostics. No unresolved cross-milestone or in-scope functional blocker remains. The review was performed by the implementing agent; no independent-agent or native-platform audit is claimed.

## Complete acceptance and TODO disposition

[Milestone 4.1](4.1.md) records actual py7zr 1.1.4 suitability, supported constraint >=1.1.4,<1.2, codecs, callback/backpressure and cleanup evidence. [Milestone 4.2](4.2.md) records integrated indexing/CLI, lifecycle, guidance and distribution evidence. The [complete implementation report](../../IMPLEMENTATION-REPORT.md) maps all 49 objective conditions individually to executable tests and retains resolved findings, excluded options, owners and actual verification limits. There is no hidden deferred accepted feature.

README covers all supported formats and eight complete Python examples, preserves the exact source-linked bytes.find excerpt and documents package/dependency buffer and close-latency limits. Root AGENTS temporary legacy reference is removed without introducing product migration history. Prior published phase/manual records remain unchanged.

## Verification

Full regression passes 687 tests with 95% production statement/branch coverage. The source is unchanged after that full run; final task edits are reports/notes only. All 134 selected package/installed/release checks pass, including exact root exports, native and independently source-rebuilt clean installations, every supported archive, all three CLI forms, protected/partial publication and eight executable README examples. Ruff lint/format over src/tests/scripts and strict src/scripts mypy pass with --no-native-parser for the known container issue.

Isolated Hatchling 1.33.0 native wheel/source builds and independent complete stable bundle name/content/checksum validation pass. Naming tests include all shared notation vectors and matching faulty expected lists; version numbers remain prohibited in every hosted asset name. Native package names inside stable bundles retain valid Python packaging identity. Actual runtime is Linux/CPython 3.12.14 with py7zr 1.1.4; native Windows/macOS/Python 3.11/big-endian checks remain unverified. No CI execution is claimed. Preparation candidates will be rebuilt from the exact eligible main release commit before tagging.

## Tracking, task composition and release coverage

Native delivery milestones #13/#14 are verified closed with exact issue sets #50–55/#56–60. T-041–T-051 are individually published/read back, with their issues closed. Each initial task completion was audited against its actual parent diff: one owning subject, substantive owned result/evidence and exactly one initial task checkbox in the same commit. T-052 adds its own reports, notes, HANDOFF and initial completion together; inspect its actual composition before integration and close issue #61 then review milestone #15 after publication/readback.

Release baseline is v0.3.0 at `2490b645891be7ae0ab7763d1aa7fe195b730b83`, selected from complete nonshallow first-parent release history before pending tag creation. Complete identities, parents, subjects and uncovered full messages through the current checkpoint were inspected; no campaign merge or revert is omitted. T-040 outcome bookkeeping adds no new product highlight. T-041–T-051 consolidate into delivered 7z behavior, constrained dependency and complete public/installed evidence. Root RELEASE-NOTES.md contains finalized body-only 0.4.0 notes; the owned ignored highlights checkpoint retains the pinned baseline/watermark until verified consumption. Refresh only pending increments through the exact final source, including the eventual two-parent integration and release commit.

## Pending authorized integration and release

After T-052 source publication/readback and issue #61/milestone #15 closure, explicitly merge the complete phase into refreshed main with two pinned parents and preserve receiving context in HANDOFF. Run the merged-state suite, commit/publish/read back the merge, then create the direct main release commit with exact root RELEASE-NOTES.md body and publish/read back it. Build, inspect, independently source-rebuild and clean-install that exact source; pass full name/inventory/content/checksum gates before tagging v0.4.0 at that source.

Use one protected release publisher. Complete hosted inventory is `archive-line-index-wheel.zip`, `archive-line-index-source.zip` and `SHA256SUMS`. Verify draft and hosted body/tag/latest/names/digests, download tag-specific assets and every advertised latest/download URL, and compare all bytes/hashes with the local inventory. Retain root notes; remove only the owned ignored highlights checkpoint after actual published body readback. Record observed merge/release identities, asset URLs/hashes and installed results here and in the implementation report/HANDOFF, publish the final outcome and stop after the complete accepted task list. Existing tags/releases and frozen records remain intact; no PyPI publication is authorized.

## Integration boundary

All 12 Phase 4 issues #50–61 and milestones #13–15 are closed after exact source publication/readback. All 12 initial task commits pass parent-diff composition audit; all 52 tasks are complete. The full branch difference contains only authorized Phase 4 work. The complete phase is merging into refreshed actual default main with receiving parent `d1d233a179cb249ddff3cc510ad89974d0ca53c2` and incoming tip `f890028d90794138ada64824b6af646903184642`, matching its recorded creation parent. No conflicts occurred. HANDOFF restores receiving main context and retains the authorized release/final stop.

Prospective merged-state verification passes all 687 tests, Ruff lint/format and strict src/scripts mypy. Maintained Markdown structure/local links and complete task audit pass. Product source matches the reviewed phase tip. The explicit merge commit and its main publication require subsequent observation.

## Verified integration and release boundary

Explicit two-parent integration `72a4e5f0c8766651a9921ccbaa259fe4d5b2397a` is published on actual default main with matching exact remote readback. Its receiving parent is `d1d233a179cb249ddff3cc510ad89974d0ca53c2` and incoming completed phase tip is `f890028d90794138ada64824b6af646903184642`. All 687 merged-state tests, Ruff and strict mypy pass; product/test source is unchanged from the reviewed phase. All 52 tasks, Phase 4 issues #50–61 and native milestones #13–15 are complete/closed. The next containing direct main release commit uses exact retained RELEASE-NOTES.md bytes as its body. Exact-source build/install/tag and actual hosted release/download verification remain pending.

## Final integration and release outcome

The complete accepted implementation is integrated and published on actual default main as `72a4e5f0c8766651a9921ccbaa259fe4d5b2397a`, with receiving parent `d1d233a179cb249ddff3cc510ad89974d0ca53c2` and incoming T-052 tip `f890028d90794138ada64824b6af646903184642`. All 687 merged-state tests, Ruff and strict src/scripts mypy pass; measured production coverage is 95%. All 52 implementation tasks and Phase 4 issues #50–61/milestones #13–15 are complete/closed. The final 12-task persistence audit verifies one substantive owned result/evidence and initial checkbox per closing commit. Frozen previous phase/manual records are preserved.

Direct main release commit `7ee4afc200c7fded93880397128b0a9e217f3c52` has the integration merge as its parent. Its raw message is exactly Release v0.4.0 followed by retained root RELEASE-NOTES.md bytes. It was published/read back before lightweight tag v0.4.0 was created and independently published/read back at that exact source. The tag remains pinned there; this later outcome commit changes documentation only.

[Archive Line Index 0.4.0](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.4.0), release ID 433519868, is published stable and confirmed as latest. One protected publisher checked complete local/draft/hosted names, source/tag/body and asset digests. All three draft assets were verified before publication; actual published body, tag, latest pointer and complete hosted inventory were read back. No CI publisher/run or PyPI upload is claimed.

## Exact-source artifacts and download verification

Isolated Hatchling 1.33.0 builds use exact release source `7ee4afc200c7fded93880397128b0a9e217f3c52`. Complete native and stable bundle name/inventory/content/checksum gates pass before tagging/publication. Each safe stable ZIP contains exactly one valid native Python package, with consistent metadata and runtime dependency py7zr>=1.1.4,<1.2. All 120 packaged tracked source/configuration/test/script/document files match that exact Git source byte for byte. The actual bundled source distribution independently rebuilds the wheel; both native and source-rebuilt wheels have observed SHA-256 `e25756ba8c6d88bfbb44780a4592ef9580c4264e4607c997e64359e6d187fb6d`.

Both actual bundle-derived variants install in clean runtimes outside the checkout without development tools or source-path injection. Each passes public streaming/index/persistence workflows, eight complete README Python examples, six plain CLI cases and 37 archive cases across console/module/imported routes. These include ZIP, every required TAR suffix, empty/late-invalid TAR, empty/normal/corrupt 7z, partial publication and real SIGINT cleanup. Actual installed dependency is py7zr 1.1.4. The earlier full-format suite separately verifies simultaneous streams, limits, consumer exceptions, real 7z progressive backpressure and worker cleanup.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| [SHA256SUMS](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.4.0/SHA256SUMS) | 191 | `398d4723fbfb22d629e89724a2c6c6838c24468eeefc154b6b41ba64b3c4f754` |
| [archive-line-index-source.zip](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.4.0/archive-line-index-source.zip) | 178918 | `34a82ded5edcaca25002b763761abb433a880c7754ff80186d84f4bc757f6ba2` |
| [archive-line-index-wheel.zip](https://github.com/pchemguy/Archive-Line-Index/releases/download/v0.4.0/archive-line-index-wheel.zip) | 38097 | `3ca5579a8e6c39a232bd738e1af6648dee374787afa86a4e44cd494a01a815bc` |

All three tag-specific assets were downloaded and their full bytes/hashes match the local inventory. Downloaded SHA256SUMS is byte-identical to the local manifest and covers both bundles. Every advertised latest/download URL was also fetched and matched the same asset bytes. Hosted identity, names and integrity are established independently of successful upload responses.

Complete Git highlights coverage remains pinned to prior v0.3.0 at `2490b645891be7ae0ab7763d1aa7fe195b730b83` through exact release source `7ee4afc200c7fded93880397128b0a9e217f3c52`. Final notes contain no checkpoint metadata and the published body matches them exactly. Root RELEASE-NOTES.md is retained. Only the owned ignored highlights checkpoint is removed after this verified published-body consumption. No functional TODO or publication effect remains unresolved; intended Windows/macOS/Python 3.11/big-endian support retains its explicitly unverified native execution status. Actual verification is Linux/CPython 3.12.14 with py7zr 1.1.4; dependency allocations and overall close latency remain outside package buffer/wait guarantees.

Phase 4 and the complete accepted implementation are finished. Publish/read back this documentation-only outcome commit, then stop; no new task/feature or external package publication is selected.
