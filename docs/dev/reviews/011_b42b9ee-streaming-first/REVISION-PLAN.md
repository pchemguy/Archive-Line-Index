# Streaming-first revision plan

## Campaign context

| Field | Value |
| --- | --- |
| Campaign | `011_b42b9ee` |
| Status | Open |
| Working branch | `revision/011_b42b9ee-streaming-first` |
| Creation parent and integration target | `main` |
| Baseline and branch-off commit | `b42b9ee8b87ba69430c0ded6e5c6edf9384c8a17` |

## Direction

Present sequential archive payload streaming as the library's primary capability and line indexing as a supporting capability. Downstream processing needs both. Assess how the README can lead with the public stream API, then explain how consumers use the line index alongside the stream.

Consider whether the existing project and package name still fits. Distinguish the displayed name, distribution name, Python import path and CLI command so the scope and compatibility cost of any proposed rename are clear. Start from the existing public API and determine whether the revised positioning can be achieved through documentation alone.

## Accepted revision

| Action | Scope | Acceptance |
| --- | --- | --- |
| R-001 | Lead with streaming in the project brief and README. Explain independent index creation, persistence, and reuse. | The public stream is the first library workflow. Consumer documentation links to both contracts and explains sequential access, ownership, and validated EOF. The archive-stream example runs against installed artifacts. |

The application owns record parsing, multiprocessing, and shared-memory transport. A combined one-pass helper and incremental offset or persisted-index APIs are deferred until a concrete downstream need establishes their contracts. Any rename remains a separate decision. The [revision report](REVISION-REPORT.md) records the assessment and verification.
