# CLI logging revision report

## Opening checkpoint

Campaign `013_833560e` opened from clean `main` at `833560e4e85fb0dc0b5c23dc41df885a4e2a976e`, matching the GitHub `main` ref. The [revision plan](REVISION-PLAN.md) records the branch, target and scope boundary.

At the baseline, the CLI defaults to INFO progress on stderr, accepts `--log-level`, and respects application handlers. After publishing this opening checkpoint, pause for the requested revision details.

## R-001 progress reporting revision

Periodic reports now use a minimum one-second interval checked at chunk boundaries. The scanner truncates its cumulative byte position to a whole multiple of the configured scan buffer, then rounds that capacity to the nearest integer in binary units with ties up. It promotes a unit if the rounded value would reach 1024. A partial buffer contributes to the exact final byte count after validated EOF and index validation. The existing CLI and caller-configured library logging share the observer.

Updated the [progress contract](../../spec/progress-logging.md), [Phase 5](../../PLAN.md#phase-5--lightweight-progress-logging), task context, design and README. Historical task completions retain their original verification evidence.

The focused logging tests showed 12 expected failures before implementation and then passed all 39 cases. Controlled clocks, short reads, BOM accounting, unit thresholds through EiB, and the real CLI adapter cover the revised reports. The full Linux suite passed 770 tests with 95% coverage. Ruff lint and format passed for 78 files, strict mypy passed for 26 source and script files, and active documentation links passed inspection.
