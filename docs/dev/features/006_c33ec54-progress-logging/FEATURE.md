# Lightweight indexing progress logging

Historical feature source/evidence. Current behavior and canonical completed task ownership are in [main SPEC](../../SPEC.md), [main PLAN](../../PLAN.md) and [main TASKS](../../TASKS.md). Retained preparation/task observations describe their recorded checkpoints; archived checklists are not executable owners.

## Purpose and observable outcome

Make long-running line-index construction observable without materially increasing scanning cost or producing per-line output. A user indexing a large plain file or supported archive can see the cumulative amount of payload processed while work is running, using Python's standard logging facility.

## Included change

Progress covers source-based `build_line_index`, direct `scan_line_offsets` and their use through the console command, module runner and imported CLI callable. Counts are cumulative uncompressed bytes processed in the operation's indexed byte space, including any initial UTF-8 BOM; they are not line counts, compressed-file positions or output-file sizes. Using the scanner's existing byte position avoids per-format accounting and supports caller-provided binary readers.

Progress observation occurs at chunk boundaries outside the LF-match loop. INFO-level updates are throttled to at most once every five seconds, followed by a final exact byte count after successful scanning. A short or empty input may produce only the final count. A final scan message describes scanning, not successful output publication; failed or interrupted scanning must not emit a successful-scan completion message. Waiting inside a source read does not generate a fabricated heartbeat.

Use named loggers in the archive_line_index namespace with ordinary LogRecord/level/handler behavior and deferred message formatting. Library APIs do not configure the root logger, install console/file handlers or change the caller's logging configuration. Callers enable, route, format and suppress progress through standard logging configuration. Default library use remains quiet.

The CLI configures concise INFO progress on stderr by default and provides logging-level control to suppress it. Logging setup belongs to invocation, not import. Repeated imported CLI calls must not accumulate handlers, duplicate records or leave unrelated application logging reconfigured. Help/usage behavior, stdout success summaries and existing failure diagnostics/statuses remain as defined by the main CLI contract, except that successful default CLI indexing now has informational progress on stderr rather than an empty stderr stream.

## Lightweight operation and retained guarantees

Keep counters/throttling state local to each scan. Disabled progress performs no per-line work, message formatting, record allocation or clock checks. Enabled progress adds only bounded per-chunk work and rate-limited records; no payload copies, extra reads, source seek/size pass, worker, dependency or growing history is introduced. Existing read bounds, LF/BOM/EOF values, direct-input borrowing, archive validation, cleanup, exceptions and independent SQLite/raw publication remain unchanged.

## Limits and non-goals

No progress bars, percentages, ETA, throughput calculation, line-by-line or byte-by-byte messages, compressed-size tracking, callbacks, background heartbeat, custom logging framework or automatic log files. This minimal change reports indexing progress; adding separate progress to standalone open_content_stream reads or row-by-row persistence is outside this feature. Standard handlers remain application-controlled and may impose their own output cost.

## Compatibility and documentation

Existing public function signatures and stored index formats remain stable. The intentional observable CLI change is INFO progress on stderr, with suppression through the selected logging-level control. Document named-logger configuration for library callers, default CLI output and suppression, byte-count meaning, throttling and completion limits. Add focused checks for exact byte totals, rate limiting, disabled cost boundaries, logging isolation and preserved results/failure behavior.

[Project scope](../../PROJECT.md), [public API design](../../decomposition/public-api.md), [line-index contract](../../spec/line-index.md) and [CLI contract](../../spec/cli.md) define retained behavior. Python's [library logging guidance](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library) informs configuration ownership. Exact logger names, CLI option spelling and formatting belong to the feature design/specification.
