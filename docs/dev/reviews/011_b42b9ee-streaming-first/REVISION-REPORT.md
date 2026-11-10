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
