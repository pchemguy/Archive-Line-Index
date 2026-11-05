# Project handoff

Campaign 009_2094900-code-docs is closed, all three review findings are Verified, and [patch release v0.5.1](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.5.1) is published stable and verified as latest. The user's requested review/plan/fix/preparation/closure/release sequence is complete; no campaign or selected task remains active. Future work awaits human direction.

[Review/recheck](reviews/009_2094900-code-docs/REVIEW-REPORT.md), [revision plan](reviews/009_2094900-code-docs/REVISION-PLAN.md) and [revision report](reviews/009_2094900-code-docs/REVISION-REPORT.md) retain frozen findings, RED/GREEN/action evidence and their then-pending effects. R-001 releases internally retained failed-read frames after successful resource closure while preserving cleanup retry and external exception evidence. R-002 reconciles current test ownership; R-003 disables Markdown hard wrapping by default. No public signature, index encoding or CLI/source-selection behavior changed. Previous closed packages/tags/releases remain unchanged.

Campaign provenance: original branch-off/receiving main 209490063eb2e299243fc7ad99e63a08305e0f3e; opening 94efdb7dc1ab5a71156f01ce9934e1a1685f92dc; final published campaign tip 96ddd9fc3a4f5e7a27c2b2fad5955b9e82f043da; verified two-parent main integration 2c351263c0be21bd088f982f702764e6b4ed4ee2. Main is the actual default branch. Direct release commit and lightweight tag v0.5.1 identify f8ab925255de8da4c3c054a938fcdb6906d1d2b3, verified on remote main first-parent history. Its literal commit body, retained RELEASE-NOTES.md and actual GitHub body are identical. GitHub release ID 435330995 is published stable/latest; the later containing outcome checkpoint does not move the tag.

Verification: full configured suite 757 passed in 52.36 seconds with 95% production statement/branch coverage; Ruff lint/format 77 files and strict mypy --no-native-parser 26 source/script files passed. Two new stream regressions observed RED/GREEN, and the 20-MiB failure probe released buffers after close while retaining the closed stream. Default Flowmark preserves long paragraph/list lines. Current links/ownership/protected-record audits passed. Exact-release-source native wheel/sdist and stable bundles passed safe content/metadata/equality/checksum plus independent complete-name gates. All 162 packaged tracked files compared byte-for-byte with the pinned source. Native and source-rebuilt installed variants each passed runtime boundaries, all nine README Python examples, six plain CLI cases and 37 archive cases. All three tag-specific and all three latest download bytes match local verified hashes.

| Release asset | SHA-256 |
| --- | --- |
| archive-line-index-source.zip | 62f9e665759c513d92fa10ef5dd04890817cb2fd1e900d30e9080015915c8a86 |
| archive-line-index-wheel.zip | 94e75593e56220c594418a13fce434e4e09bf1e14d75186b59891b252bacc337 |
| SHA256SUMS | ef16eca85c8af5f0a35f299237faa03f39336bca5a89c72785f168731a59fa94 |

Actual execution was Linux/CPython 3.12.14 with py7zr 1.1.4. Native Windows/macOS/other Python/big-endian execution remains unverified. Existing cooperative 7z cancellation, dependency-controlled allocation and observable-only ZIP validation limits remain explicit. No hosted CI/native compatibility or new throughput/close-latency guarantee is claimed.

The owned ignored highlights checkpoint was consumed by exact published-body readback and removed; RELEASE-NOTES.md remains. No release/campaign effect remains pending. The containing outcome-only main checkpoint requires its own final publication/readback and clean status confirmation, then stop. Keep closed campaign records frozen and Markdown unwrapped.
