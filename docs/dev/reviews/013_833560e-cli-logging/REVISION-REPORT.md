# CLI logging revision report

## Opening checkpoint

Campaign `013_833560e` opened from clean `main` at `833560e4e85fb0dc0b5c23dc41df885a4e2a976e`, matching the GitHub `main` ref. The [revision plan](REVISION-PLAN.md) records the branch, target and scope boundary.

At the baseline, the CLI defaults to INFO progress on stderr, accepts `--log-level`, and respects application handlers. After publishing this opening checkpoint, pause for the requested revision details.

## R-001 progress reporting revision

Periodic reports now use a minimum one-second interval checked at chunk boundaries. The scanner truncates its cumulative byte position to a whole multiple of the configured scan buffer, then rounds that capacity to the nearest integer in binary units with ties up. It promotes a unit if the rounded value would reach 1024. A partial buffer contributes to the exact final byte count after validated EOF and index validation. The existing CLI and caller-configured library logging share the observer.

Updated the [progress contract](../../spec/progress-logging.md), [Phase 5](../../PLAN.md#phase-5--lightweight-progress-logging), task context, design and README. Historical task completions retain their original verification evidence.

The focused logging tests showed 12 expected failures before implementation and then passed all 39 cases. Controlled clocks, short reads, BOM accounting, unit thresholds through EiB, and the real CLI adapter cover the revised reports. The full Linux suite passed 770 tests with 95% coverage. Ruff lint and format passed for 78 files, strict mypy passed for 26 source and script files, and active documentation links passed inspection.

## R-002 buffer-based display precision

Replaced R-001's integer-only periodic formatting with the fewest decimal places needed for the last displayed digit to represent at most 100 scan buffers. Rounding uses integer arithmetic and ties round up. Trailing zeros retain the chosen precision. If rounding reaches 1024, the formatter promotes the unit and recalculates its precision. The default 1 MiB buffer produces whole MiB and two decimal places for GiB. Periodic timing, complete-buffer accounting and the exact final byte count carry forward.

Eight of the eleven precision cases failed against the integer-only formatter. All 42 focused logging and CLI checks passed after the change, and the full Linux suite passed 773 tests with 95% coverage. Ruff, strict mypy, and active documentation link checks passed.

## R-003 elapsed scan time

Successful scans retain the exact-byte completion record and then emit elapsed scan time in seconds to two decimal places. The original monotonic start is preserved independently of the last periodic report. Timing ends after EOF and index validation, before source cleanup or persistence. Failure and disabled-INFO behavior were verified. Updated the README, Phase 5 and its current design and contracts.

Nine focused cases failed before implementation. Afterward, all 141 focused logging, CLI and installed-archive tests passed. The full Linux suite passed 773 tests with 95% coverage. Ruff lint and format, strict mypy and changed-document link checks passed.
