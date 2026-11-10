# Streaming-first revision report

## Opening checkpoint

Campaign `011_b42b9ee` opened on `revision/011_b42b9ee-streaming-first` from `main` at `b42b9ee8b87ba69430c0ded6e5c6edf9384c8a17`. The starting worktree was clean, remote `main` matched the baseline, and campaign 010 was the highest allocated sequence.

At the baseline, the [README](../../../../README.md) leads with line indexing and presents its streaming walkthrough later. The existing [public API](../../spec/public-api.md) already exposes independent sequential payload access through `open_content_stream` and index construction through `build_line_index`. The [revision plan](REVISION-PLAN.md) records the requested emphasis and the pending naming decision.

Opening verification covers changed paths, record links, whitespace and branch ancestry. After publication is verified, pause before drafting or applying revisions.

## R-001 streaming-first documentation

The [architecture](../../ARCHITECTURE.md) and [content stream contract](../../spec/content-stream.md) already define standalone, bounded payload access. Index building composes the existing stream and scanner. The user accepted keeping indexing independent and leaving parser orchestration downstream.

Updated the [project brief](../../PROJECT.md) and [README](../../../../README.md). The README puts a ZIP streaming example before the indexing walkthrough and links the stream contract from the integration table. It explains that independent reads and index construction make separate passes, and that downstream publication can wait for validated EOF. A combined helper and incremental index APIs await demonstrated demand. Naming remains undecided.

Both installed-artifact documentation tests and 32 stream, lifecycle, and backpressure tests passed. README local links and section order passed inspection. The campaign remains open.

Clarified the opening of both documents to state the main purpose explicitly: transparent streaming of uncompressed files and compressed archive payloads through one interface with automatic reader and decompressor selection. Verified identical payload bytes from all six Alphanum fixtures using bounded reads through `open_content_stream(path)`.

## R-002 rename planning

Mapped the current display, distribution, import, console, logger and artifact names to their code, packaging, test, documentation and demo owners. The [revision plan](REVISION-PLAN.md#archive-stream-rename-proposal) records the proposed Archive Stream cutover, the retained index command, the old-to-new installation sequence and a verification matrix. Implementation awaits acceptance.

Baseline verification at `d082938b68016189372aaeb0bdb96f01b4c9d498` on Linux passed all 757 tests with the existing package names. No rename work was executed at this planning checkpoint.

## R-002 rename execution

The user accepted Archive Stream and authorized the cutover. Moved all 23 production files under `src/archive_stream/` and updated the distribution, module runner, logger name, build and coverage settings, release bundles, test imports and assertions, consumer documentation, and demos. The console command `archive-line-index` loads `archive_stream.cli:main`. The existing v0.5.1 release remains the previous distribution. Checkout installation is documented for the renamed package pending a separate release.

The updated wheel metadata and hosted inventory checks first failed against the old names and passed after the cutover. The full suite passed 757 tests with 95% coverage, including both the native wheel and sdist-rebuilt wheel installed outside the checkout. Ruff lint and format passed on 78 files and strict mypy passed on 26 source and script files. The native artifact, stable-bundle, checksum and independent complete-name gates passed. All 23 staged package files matched their bytes inside both native artifacts.

An isolated install of the wheel built from tag v0.5.1, followed by uninstall and installation of the renamed candidate, restored the retained command with the new import and produced byte-identical SQLite and raw indexes for both plain and 7z inputs. Checkout CLI/API parity passed for all six Alphanum fixtures. Windows launcher commands and CRLF checkout were checked, with native CMD execution still unverified. The active-name and link audit and independent cutover review found no critical or important issues. Frozen campaign records and the published release evidence were preserved.
