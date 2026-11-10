# Progress logging contract

The [component design](../DECOMPOSITION.md) assigns observation to the scanner and invocation configuration to the CLI. This contract defines standard logging behavior alongside [line indexing](line-index.md) and the [CLI contract](cli.md). Public function signatures and index formats remain unchanged.

## Scan records and cost

Emit INFO records from archive_stream.scanner. Periodic records use the cumulative uncompressed scan position rounded down to a multiple of the configured `buffer_size`. Accumulate short reads and BOM-probe bytes in the same byte coordinate. A report can repeat a value or show zero while the current buffer is incomplete. Display the completed capacity as a whole number in B, KiB, MiB, GiB, TiB, PiB or EiB. Round to the nearest integer with ties up, selecting the first unit whose rounded value is less than 1024.

The final record reports the exact EOF byte count, including any incomplete buffer and any skipped BOM. Counts start at local zero for borrowed readers. Empty input finishes at zero and BOM-only input at three. Exact prose and record formatting may change.

Snapshot whether INFO is enabled when constructing the scan observer. When disabled, perform no clock reads, record creation or message formatting; only constant per-chunk observer checks are permitted. When enabled, initialize the last-report monotonic time once and check elapsed time after each processed nonempty chunk, including the assembled initial prefix. Emit a periodic record only when at least 1.0 second has elapsed since initialization or the previous periodic record, then update that report time. Do not catch up missed intervals or run a heartbeat during blocking reads. A final record is additional to the periodic rate limit and occurs only after validated EOF and completed-array validation. Failure/interruption before that point emits no successful-scan completion. Prior periodic records remain observations of processed prefixes, not integrity certification.

Keep observer state local to a scan. No new source reads, seeking, payload copies, workers, per-byte/per-line operations, dependencies or unbounded log history are permitted. Standard logging filters/handlers continue to govern record delivery and may have application-controlled costs or failures. The package does not suppress arbitrary custom-handler exceptions. Existing stream/array ownership, cleanup, byte/offset semantics and persistence behavior remain unchanged.

## CLI configuration

Add --log-level LEVEL with case-insensitive DEBUG, INFO, WARNING, ERROR or CRITICAL choices and default INFO. Invalid levels are usage errors with status 2 before source/output inspection. INFO enables progress; WARNING and higher suppress it. DEBUG does not enable extra per-line reporting. Help/usage performs no logging configuration, source inspection or indexing.

During the scan, set only the archive_stream.scanner logger's level to the selected value and restore its prior explicit level even on error/interruption. Controlling the emitting scanner logger also enforces WARNING suppression when the application previously gave that child an explicit INFO level. Respect its existing propagation/disabled state and all application handlers. If logger.hasHandlers() is true, add no handler; those effective handlers determine destination/format/filtering, including intentional NullHandler suppression. Otherwise attach one owned StreamHandler using the current stderr and format %(levelname)s: %(message)s, removing and closing it on exit. Never replace or reformat application handlers, configure root logging, or accumulate handlers across serialized imported calls. Library imports/scans do not configure logging. Concurrent application logging configuration/CLI invocations must be serialized by the caller; independent library scans retain local progress state.

The stdout summary, help/usage streams, operational/interruption statuses and failure/publication diagnostics remain unchanged. Default standalone console/module/imported execution now emits scan progress on stderr; successful stderr is no longer guaranteed empty. Application-configured handlers can route progress elsewhere. --log-level WARNING retains quiet progress behavior while preserving errors. A scan-complete message may precede a later persistence failure and never means paired output publication succeeded.

## Acceptance

| ID | Observable condition |
| --- | --- |
| LOG-01 | Plain/archive source builds and direct short-read scans produce unchanged canonical offsets; Final INFO records report exact uncompressed byte counts, including empty and BOM-only inputs. |
| LOG-02 | Controlled monotonic times demonstrate no periodic record before one second, one when due and no catch-up burst. Complete-buffer counts cover short reads and the BOM probe. Rounded units handle ties and promotion at 1024. Final bytes are exact, and separate scans retain independent state. |
| LOG-03 | Disabled INFO performs no clock/record work; dense versus sparse LF input with the same chunking has the same observation cost rather than per-line work. Read bounds and borrowed-input ownership remain unchanged. |
| LOG-04 | Read, terminal, index-validation or interruption failures do not emit scan-complete; source-building cleanup and no output-after-source-failure still hold. |
| LOG-05 | All CLI routes expose the log-level option, default progress and WARNING suppression; invalid/help paths do no work, and original summaries/statuses/persistence results remain correct. |
| LOG-06 | Existing root/package handlers, levels, formatters, propagation and unrelated logging are preserved outside invocation; repeated calls introduce no duplicate handlers, and cleanup/restoration occurs on failure/interruption. |
| LOG-07 | Documentation explains one-second timing, complete-buffer binary units and scan versus publication. Installed wheel and source-rebuilt workflows verify configuration, suppression and exact final byte counts. |
