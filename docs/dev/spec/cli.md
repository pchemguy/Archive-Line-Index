# Single-target CLI contract

## Entry points and invocation

The CLI adapter in [DECOMPOSITION](../DECOMPOSITION.md) implements the callable and execution entry points declared in [public API design](../decomposition/public-api.md). The installed command, module runner and imported callable share one parser and execution path.

```text
archive-line-index TARGET [-o OUTPUT_STEM | --output OUTPUT_STEM] [--overwrite]
python -m archive_line_index TARGET [-o OUTPUT_STEM | --output OUTPUT_STEM] [--overwrite]
```

Exactly one target is required. `-h`/`--help` displays usage and returns success without path inspection or indexing. Missing/extra positional targets, unknown options and a missing output-option value are usage errors. Standard `--` ends option parsing for a target whose name starts with a hyphen. Shell quoting and explicit argv elements preserve paths containing spaces.

There are no subcommands, recursive/batch processing, stdin payloads, progress UI, single-format selection, source mutation or configuration-file discovery. Both index formats are produced from one completed array. The CLI uses the library defaults for BOM handling, buffer size and decompressed-size limit.

## Output names and execution

With no output option, use the target directory and filename stem, appending `.sqlite3` for SQLite and `.u64` for raw little-endian binary. For example, `data/events.zip` produces `data/events.sqlite3` and `data/events.u64`. The stem removes the final suffix under normal path semantics: `events.tar.gz` has stem `events.tar`, an extensionless `events` has stem `events`, and a dotfile without a suffix retains its name.

An explicit `--output OUTPUT_STEM` supplies a shared path stem, not a single output filename or directory. `--output results/custom` produces `results/custom.sqlite3` and `results/custom.u64`; the two extensions are appended to the supplied stem. Relative paths are relative to the current working directory. Parent directories are not created automatically.

Before scanning, preflight both output paths. Reject any output naming the source itself or an existing alias of it, including a hard link or symlink alias, even with `--overwrite`. Compare lexical absolute paths and filesystem same-file identity when the relevant paths exist. If default naming collides with the source, an explicit distinct output stem is required. Without `--overwrite`, either protected existing output, including a dangling symlink, fails before index construction or either write. `--overwrite` authorizes replacement only of distinct output paths. Preflight does not replace each writer's publication-time protection; concurrent external source/path changes remain outside the stable-input assumption.

After parsing and preflight, call `build_line_index` once for the target. Pass the same completed array first to `write_sqlite_index`, then to `write_raw_index`. Do not rescan or reopen the payload to produce the second format. The two outputs contain exactly the same logical offsets and EOF sentinel. Do not call either writer after source/index failure or extract members to disk. The CLI owns its result array; the library owns stream, worker, database and temporary-file cleanup.

Each output follows the independent [persistence contract](persistence.md). There is no two-output transaction or rollback of an already published file. If SQLite fails, do not start the raw write. If SQLite succeeds but raw fails, retain the completed SQLite output and report the raw failure plus the already published SQLite path. A writer's post-publication cleanup failure also retains its completed output and publication note; execution stops before any later writer. Both paths are preflighted up front, but publication-time races or later failures can still leave one updated output and another absent or unchanged.

## Importable execution

```python
from archive_line_index.cli import main

status = main(["data/events.zip"])
```

An explicit argv value is a sequence of strings, not a command-line string; an invalid Python argument kind raises `TypeError` before parsing or I/O. `main(None)` reads `sys.argv[1:]`. Importing the package, CLI module or module-runner module does not parse arguments, read argv, open paths, print output or exit the process.

The callable returns an integer for the outcomes below and does not raise `SystemExit` for parser help/errors or expected operational failures. It uses the current standard output/error streams without replacing them permanently. Console and executable module wrappers alone convert the returned integer into a process exit status. Unexpected programming errors are not silently converted into a success result.

## Output and status

| Outcome | Status | Required output and side effects |
| --- | --- | --- |
| Both index writes and their cleanup succeed | 0 | One concise stdout summary identifying both output paths and line count `len(offsets) - 1`; no payload or full offset-array dump. Stderr is empty. |
| Help | 0 | Usage/help on stdout; no source/output inspection or mutation. |
| Usage error | 2 | Usage and a concise diagnostic on stderr; stdout is empty; no source/output inspection or mutation. |
| Expected indexing, validation or filesystem failure | 1 | A concise diagnostic on stderr, no traceback by default and no success summary. Identify any output already published before the failure. Source/destination alias rejection is an operational failure. |
| Keyboard interruption during work | 130 | A concise interruption diagnostic on stderr, no success summary, library cleanup on unwinding and identification of any known completed publication. |

Expected operational failures include package exceptions, ordinary filesystem errors and memory exhaustion. Reports retain relevant exception notes, including a writer's explicit notice that publication succeeded before cleanup failed. A nonzero status after publication does not mean all outputs are absent or rolled back. Exact diagnostic wording is not a stable contract. Library entry points continue to raise Python exceptions directly and do not acquire CLI printing or process-exit behavior.

## Acceptance

- CLI-01: Console, module and imported callable paths index one plain or supported archive target into equivalent canonical SQLite/raw pairs and report the correct line count, including empty/BOM-only inputs. The payload is indexed once for both outputs.
- CLI-02: Default naming uses the input directory and filename stem with `.sqlite3`/`.u64`; explicit output stem, compound/absent suffixes, dotfiles, spaces in paths and `--` for a hyphen-prefixed target work under the stated path rules.
- CLI-03: Help/usage errors return their specified statuses without opening or inspecting target/output paths; importing each entry module performs no CLI work and the callable never exits the caller for these outcomes.
- CLI-04: Either protected existing output or a source/output alias is rejected before scanning or writing; explicit overwrite replaces only distinct outputs through the existing publication guarantees.
- CLI-05: Source, archive, index and either writer failure produce nonzero status and stderr without a success summary. SQLite failure prevents the raw write; raw failure retains and identifies completed SQLite output; post-publication cleanup failure reports the publication note, and interruption releases owned resources.
- CLI-06: Installed execution outside the checkout exposes the console command, `python -m` runner and importable callable without development dependencies or source-path injection, and both persisted outputs load through their independent library readers.
