# Progress logging component design

[FEATURE](FEATURE.md) extends the accepted main [architecture](ARCHITECTURE.md) and [component design](DECOMPOSITION.md) without changing public function signatures.

## Owners and collaboration

The scanner owns named logger archive_line_index.scanner and an operation-local private _ScanProgress observer in scanner.py. It consumes only an absolute processed-byte position already computed by the scanner. update(position) checks a monotonic clock at chunk boundaries when INFO was enabled for this scan; finish(position) emits the final total only after EOF and offset validation. Five-second throttling state is local, with no shared counter, worker, callback API, payload storage or per-LF observation. No new production module is needed.

The CLI owns --log-level and a scoped private _progress_logging(level) context in cli.py, used around index construction after argument parsing and output preflight. It obtains package logger archive_line_index, temporarily selects the requested level, and uses effective existing handlers if any are configured. Otherwise it attaches one temporary StreamHandler to the invocation's stderr with a concise INFO: message format. It removes/closes only its own handler and restores the previous package level on every exit. Root settings, existing handlers/formatters/propagation and unrelated loggers remain caller-owned; no forceful basicConfig or import-time output/configuration is permitted. Application-configured handlers may intentionally route or suppress messages instead of stderr. Repeated CLI invocations are serialized when configuring shared logging, as ordinary application logging configuration requires.

The existing main callable still owns parser statuses, diagnostics and paired writer ordering; executable wrappers remain thin. Library callers configure logging themselves. No logger/observer is a new package-root export. The source facade, adapters, stream, offset model and persistence require no progress implementation. A final scan event is distinct from index publication success.

## Chosen approach and limits

Uncompressed scanner positions cover both filesystem/archive builders and borrowed-reader scans. Compressed positions would require adapter-specific accounting and would not cover arbitrary readers; stream-layer logging alone would miss direct scans or duplicate scanner reporting. Chunk-boundary observation plus a monotonic interval avoids per-line overhead and a background heartbeat. Existing custom handlers retain normal Python logging behavior; application handler failures are not swallowed or transformed into a new package exception. The scanner still borrows inputs and source-based building still unwinds owned resources.
