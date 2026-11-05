# Revision report

Campaign 009_2094900-code-docs; [plan](REVISION-PLAN.md), [review findings](REVIEW-REPORT.md); baseline 209490063eb2e299243fc7ad99e63a08305e0f3e. The user authorized all three repairs, 0.5.1 preparation, campaign closure/integration and release publication. Opening state was planned; completed actions and checks follow. Actual RED/GREEN, doc/config checks, release preparation and subsequent effects will be recorded as performed.

## V-001 — Failed-read resource lifetime

Added two regressions: a weak-reference marker proves failed unbounded-read frames become reclaimable after successful close while the closed stream remains referenced; a separate case proves failed cleanup retains the original failure until successful retry and does not mutate externally held traceback/notes. Observed RED before source edit: frame-reclamation assertion failed; the retry/exception characterization passed.

ContentStream.close now drops its retained failure reference only after reader release succeeds, leaving caller-owned exception objects untouched. GREEN: 90 stream/API/progress/full-format lifecycle cases passed in 2.08 seconds. The original 20-MiB probe changed from 20,974,172 live bytes before close to 880 after close, retaining the closed stream. Ruff lint/format pass after shortening one test name to meet formatter style; the initial format-only failure was corrected. R-001 is repaired and verified for this action; final coupled checks remain.

## V-002 — Current test ownership

Replaced nonexistent index-building/resource-lifecycle allocation names with actual plain/archive workflow, cross-format lifecycle and 7z/backpressure owners. Clarified root versus integration fixture ownership and added installed CLI, safe-path/plugin prerequisites and release-helper test owners. Every delivered test module name is represented; every concrete integration path listed in the table resolves. Responsibility descriptions were compared with current test scenarios. Only the current layout map changed; no empty test files, requirement change or closed-record edit. R-002 is verified by map/path inspection; no runtime test was needed for this documentation-only action.

## V-003 — Formatter policy alignment

Set tool.flowmark.width to 0 while retaining semantic=false and all other Markdown settings. A stdin/stdout probe with a heading, long paragraph and long list item used the project-default formatter without a width override; all nonempty source lines were preserved exactly. No Markdown file was reformatted and no closed record changed. R-003 is repaired and verified; final configured tools/package checks follow with V-004.

## V-004 — Coupled verification and patch preparation

Prepared version 0.5.1 in static metadata and current README install/check commands. RELEASE-NOTES.md includes the runtime closure fix, current test map, formatter default, integrated README/navigation and earlier logging-test hardening since v0.5.0, with unchanged interface/format/CLI compatibility and actual native limits. Complete Git identity/parent/subject inventory since v0.5.0 was inspected, using campaign 007/008 integration summaries first and direct campaign 009 source/evidence for its new changes; prior release outcome bookkeeping adds no runtime highlight. The ignored highlights checkpoint retains coverage and awaits incremental refresh through finalization/merge/release source.

Final configured suite: 757 passed, 95% production statement/branch coverage. Ruff lint/format over 77 files and strict mypy --no-native-parser over 26 files pass. Actual 0.5.1 native builds and stable bundle checks pass safe content/metadata/source-wheel equality/checksum plus independent complete-name checks for all three outer assets. Nine README Python examples execute in native/source-rebuilt installed consumers. Two new stream regressions supplement the prior 755 cases. All findings are Verified; current contract links, ownership references, unwrapped Markdown policy and protected-record scope checks pass. Candidate packages are preparation only and will be rebuilt from the final exact default-branch release commit.

## Finalization and closure boundary

The user authorized closing this campaign and publishing 0.5.1. Original opening 94efdb7dc1ab5a71156f01ce9934e1a1685f92dc and full branch-off/receiving main baseline 209490063eb2e299243fc7ad99e63a08305e0f3e remain unchanged. V-001 dae29f38442b34dfacf60e901823eb3cb4324483, V-002 411abb3fc934645e99b918fe79f28e172c6f2456 and V-003 75a127d77838bf750f08e45eeececd21469c6557 were individually published/read back. The containing V-004/finalization checkpoint requires publication, followed by explicit two-parent main integration and merged verification/readback; that closes the selected repair campaign. Git integration evidence and current HANDOFF own subsequent effects, so do not retrofit release results into this frozen campaign afterward.

Release 0.5.1 is prepared but not yet tagged/published. After closure, use a direct default-branch release commit whose literal body equals RELEASE-NOTES.md, rebuild final source/wheel stable bundles, check exact source/installed/rebuilt consumers, publish/read back tag v0.5.1, create/reuse one draft, upload/verify all three assets, publish stable/latest and compare all tag-specific/latest download bytes. Preserve existing tags/releases. Linux/CPython 3.12.14/py7zr 1.1.4 only; native Windows/macOS/other Python/big-endian remain unverified.
