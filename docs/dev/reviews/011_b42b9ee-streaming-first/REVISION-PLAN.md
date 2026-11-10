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

## Next decision

The opening checkpoint records the direction. README changes, any rename and any code changes are pending decisions. The [revision report](REVISION-REPORT.md) records the baseline and subsequent verification.
