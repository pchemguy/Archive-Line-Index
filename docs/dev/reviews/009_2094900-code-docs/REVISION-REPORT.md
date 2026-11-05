# Revision report

Campaign 009_2094900-code-docs; [plan](REVISION-PLAN.md), [review findings](REVIEW-REPORT.md); baseline 209490063eb2e299243fc7ad99e63a08305e0f3e. The user authorized all three repairs, 0.5.1 preparation, campaign closure/integration and release publication. State: planned; no repair or new check claimed at this checkpoint. Actual RED/GREEN, doc/config checks, release preparation and subsequent effects will be recorded as performed.

## V-001 — Failed-read resource lifetime

Added two regressions: a weak-reference marker proves failed unbounded-read frames become reclaimable after successful close while the closed stream remains referenced; a separate case proves failed cleanup retains the original failure until successful retry and does not mutate externally held traceback/notes. Observed RED before source edit: frame-reclamation assertion failed; the retry/exception characterization passed.

ContentStream.close now drops its retained failure reference only after reader release succeeds, leaving caller-owned exception objects untouched. GREEN: 90 stream/API/progress/full-format lifecycle cases passed in 2.08 seconds. The original 20-MiB probe changed from 20,974,172 live bytes before close to 880 after close, retaining the closed stream. Ruff lint/format pass after shortening one test name to meet formatter style; the initial format-only failure was corrected. R-001 is repaired and verified for this action; final coupled checks remain.
