# Revision report

Campaign 009_2094900-code-docs; [plan](REVISION-PLAN.md), [review findings](REVIEW-REPORT.md); baseline 209490063eb2e299243fc7ad99e63a08305e0f3e. The user authorized all three repairs, 0.5.1 preparation, campaign closure/integration and release publication. State: planned; no repair or new check claimed at this checkpoint. Actual RED/GREEN, doc/config checks, release preparation and subsequent effects will be recorded as performed.

## V-001 — Failed-read resource lifetime

Added two regressions: a weak-reference marker proves failed unbounded-read frames become reclaimable after successful close while the closed stream remains referenced; a separate case proves failed cleanup retains the original failure until successful retry and does not mutate externally held traceback/notes. Observed RED before source edit: frame-reclamation assertion failed; the retry/exception characterization passed.

ContentStream.close now drops its retained failure reference only after reader release succeeds, leaving caller-owned exception objects untouched. GREEN: 90 stream/API/progress/full-format lifecycle cases passed in 2.08 seconds. The original 20-MiB probe changed from 20,974,172 live bytes before close to 880 after close, retaining the closed stream. Ruff lint/format pass after shortening one test name to meet formatter style; the initial format-only failure was corrected. R-001 is repaired and verified for this action; final coupled checks remain.

## V-002 — Current test ownership

Replaced nonexistent index-building/resource-lifecycle allocation names with actual plain/archive workflow, cross-format lifecycle and 7z/backpressure owners. Clarified root versus integration fixture ownership and added installed CLI, safe-path/plugin prerequisites and release-helper test owners. Every delivered test module name is represented; every concrete integration path listed in the table resolves. Responsibility descriptions were compared with current test scenarios. Only the current layout map changed; no empty test files, requirement change or closed-record edit. R-002 is verified by map/path inspection; no runtime test was needed for this documentation-only action.

## V-003 — Formatter policy alignment

Set tool.flowmark.width to 0 while retaining semantic=false and all other Markdown settings. A stdin/stdout probe with a heading, long paragraph and long list item used the project-default formatter without a width override; all nonempty source lines were preserved exactly. No Markdown file was reformatted and no closed record changed. R-003 is repaired and verified; final configured tools/package checks follow with V-004.
