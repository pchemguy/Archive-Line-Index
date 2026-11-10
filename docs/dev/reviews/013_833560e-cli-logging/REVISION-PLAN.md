# CLI logging revision plan

| Field | Value |
| --- | --- |
| Campaign | `013_833560e` |
| Status | Open |
| Working branch | `revision/013_833560e-cli-logging` |
| Creation parent and integration target | `main` |
| Baseline and branch-off commit | `833560e4e85fb0dc0b5c23dc41df885a4e2a976e` |

The user requested a one-second periodic interval, reporting only the cumulative capacity of complete scan buffers in rounded binary units, with the final report kept exact. Incorporate the change into existing Phase 5 in [PLAN](../../PLAN.md) and [TASKS](../../TASKS.md). The [CLI contract](../../spec/cli.md) and [progress logging contract](../../spec/progress-logging.md) own current behavior.

| Action | Scope | Acceptance |
| --- | --- | --- |
| R-001 | Revise the shared scanner observer used by the CLI and library and reconcile the existing logging design, contracts, phase and README. | Check elapsed time at chunk boundaries. Truncate the original-byte position to a whole multiple of the configured buffer size, even across short reads and the BOM probe. Round binary units to integers with ties up and promote any value that would round to 1024. Retain the exact byte count and validation boundary for completion. |
| R-002 | Refine periodic display precision based on the configured scan buffer. | Use the fewest decimal places that make the last digit represent at most 100 buffers. Keep trailing zeros and round ties up. Recompute precision when promoting a displayed 1024 into the next unit. |

The [revision report](REVISION-REPORT.md) records the opening checkpoint.
