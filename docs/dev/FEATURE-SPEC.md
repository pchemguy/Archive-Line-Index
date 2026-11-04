# Indexing progress specification

This delta implements [FEATURE](FEATURE.md) and [component design](FEATURE_DECOMPOSITION.md). Main [SPEC](SPEC.md), [line-index](spec/line-index.md) and [CLI](spec/cli.md) contracts remain normative except for the explicit logging/CLI additions here.

## Scan records and cost

Emit INFO records from archive_line_index.scanner. Periodic messages describe cumulative uncompressed bytes scanned; successful terminal messages identify scan completion and the exact EOF byte coordinate. Counts include skipped BOM bytes, start at local zero for borrowed readers and increase monotonically within each scan. Empty input finishes at zero and BOM-only input at three. No record contains payload bytes or a per-line dump. Exact prose/format is not a public parsing API.

Snapshot whether INFO is enabled when constructing the scan observer. When disabled, perform no clock reads, record creation or message formatting; only constant per-chunk observer checks are permitted. When enabled, initialize the last-report monotonic time once and check elapsed time after each processed nonempty chunk, including the assembled initial prefix. Emit a periodic record only when at least 5.0 seconds have elapsed since initialization or the previous periodic record, then update that report time. Do not catch up missed intervals or run a heartbeat during blocking reads. A final record is additional to the periodic rate limit and occurs only after validated EOF and completed-array validation. Failure/interruption before that point emits no successful-scan completion. Prior periodic records remain observations of processed prefixes, not integrity certification.

Keep observer state local to a scan. No new source reads, seeking, payload copies, workers, per-byte/per-line operations, dependencies or unbounded log history are permitted. Standard logging filters/handlers continue to govern record delivery and may have application-controlled costs or failures. The package does not suppress arbitrary custom-handler exceptions. Existing stream/array ownership, cleanup, byte/offset semantics and persistence behavior remain unchanged.

## CLI configuration

Add --log-level LEVEL with case-insensitive DEBUG, INFO, WARNING, ERROR or CRITICAL choices and default INFO. Invalid levels are usage errors with status 2 before source/output inspection. INFO enables progress; WARNING and higher suppress it. DEBUG does not enable extra per-line reporting. Help/usage performs no logging configuration, source inspection or indexing.

During the scan, set only the archive_line_index.scanner logger's level to the selected value and restore its prior explicit level even on error/interruption. Controlling the emitting scanner logger also enforces WARNING suppression when the application previously gave that child an explicit INFO level. Respect its existing propagation/disabled state and all application handlers. If logger.hasHandlers() is true, add no handler; those effective handlers determine destination/format/filtering, including intentional NullHandler suppression. Otherwise attach one owned StreamHandler using the current stderr and format %(levelname)s: %(message)s, removing and closing it on exit. Never replace or reformat application handlers, configure root logging, or accumulate handlers across serialized imported calls. Library imports/scans do not configure logging. Concurrent application logging configuration/CLI invocations must be serialized by the caller; independent library scans retain local progress state.

The stdout summary, help/usage streams, operational/interruption statuses and failure/publication diagnostics remain unchanged. Default standalone console/module/imported execution now emits scan progress on stderr; successful stderr is no longer guaranteed empty. Application-configured handlers can route progress elsewhere. --log-level WARNING retains quiet progress behavior while preserving errors. A scan-complete message may precede a later persistence failure and never means paired output publication succeeded.

## Acceptance

| ID | Observable condition |
| --- | --- |
| LOG-01 | Plain/archive source builds and direct short-read scans produce unchanged canonical offsets; INFO records report exact cumulative uncompressed totals, including empty/BOM inputs. |
| LOG-02 | Controlled monotonic times demonstrate no periodic record before five seconds, one when due, no catch-up burst and an exact successful final record. Separate scans do not share counters or timing state. |
| LOG-03 | Disabled INFO performs no clock/record work; dense versus sparse LF input with the same chunking has the same observation cost rather than per-line work. Read bounds and borrowed-input ownership remain unchanged. |
| LOG-04 | Read, terminal, index-validation or interruption failures do not emit scan-complete; source-building cleanup and no output-after-source-failure still hold. |
| LOG-05 | All CLI routes expose the log-level option, default progress and WARNING suppression; invalid/help paths do no work, and original summaries/statuses/persistence results remain correct. |
| LOG-06 | Existing root/package handlers, levels, formatters, propagation and unrelated logging are preserved outside invocation; repeated calls introduce no duplicate handlers, and cleanup/restoration occurs on failure/interruption. |
| LOG-07 | Documentation and actual wheel/source-rebuilt installed use demonstrate configuration/suppression, five-second chunk-based timing, count meaning and scan-versus-publication limits. |
