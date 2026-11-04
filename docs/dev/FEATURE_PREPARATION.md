# Feature preparation record

## Identity and request

Campaign 006_c33ec54; descriptive association 006_c33ec54-progress-logging. Full starting baseline and recorded creation parent main: c33ec544e06134ab71866a4bf2f46ad21c9d150d. Actual preparation branch design-docs/006_c33ec54-progress-logging; default preparation/integration target main. Intended later implementation parent main containing the verified preparation merge; intended implementation branch feature/006_c33ec54-progress-logging, not yet created. Reserve docs/dev/features/006_c33ec54-progress-logging/ for eligible future reports/archive; active feature sources belong in docs/dev, without a placeholder navigation package.

The human requested opening a feature campaign for minimal lightweight progress on large sources, cumulative uncompressed or compressed bytes using whichever needs less new code, no per-line progress, proper standard Python logging. The follow-up confirms five-second increments. No implementation range or future document-checkpoint preapproval was supplied. Retain baseline 0.4.1 functionality, frozen campaigns 001–005, original task/hosted closures and releases.

Active sources: [feature documentation tasks](FEATURE_DOCS_TASKS.md), this record and [HANDOFF](HANDOFF.md). [FEATURE](FEATURE.md) is now the published-for-review proposal; its first approval is pending. Affected main context is PROJECT, ARCHITECTURE, DECOMPOSITION and public API design, SPEC's line-index/public-operation/CLI contracts, PLAN/layout, scanner/api/cli and their tests. These are current reference inputs, not amended by opening.

## Current control

Interactive/onepass, pass 1, strict delivery; selected by established interactive workflow and no new mode override. One bounded scope: lightweight indexing progress. First FEATURE approval and later applicable checkpoints remain active. The human's five-second amendment settles that cadence only; it does not accept an unseen brief or implementation plan. Current stage FDOCS-002: publish/read back the FEATURE proposal and await first approval before dependent design/specification. FDOCS-001 publication and issue closure are verified.

Root AGENTS enables GitHub tracking throughout documentation/implementation by default. The pre-write gate is verified before this branch/ref and repository writes: [milestone #16](https://github.com/pchemguy/Archive-Line-Index/milestone/16) is open and all nine campaign-qualified stage issues have matching titles, opening/closing task markers, feature-scope marker and native milestone association. Their complete briefs came from the pinned bundled FEATURE_DOCS_TASKS_TEMPLATE, not product task-list inference.

| Stage | Hosted issue |
| --- | --- |
| FDOCS-001 | [#63](https://github.com/pchemguy/Archive-Line-Index/issues/63) |
| FDOCS-002 | [#64](https://github.com/pchemguy/Archive-Line-Index/issues/64) |
| FDOCS-003 | [#65](https://github.com/pchemguy/Archive-Line-Index/issues/65) |
| FDOCS-004 | [#66](https://github.com/pchemguy/Archive-Line-Index/issues/66) |
| FDOCS-005 | [#67](https://github.com/pchemguy/Archive-Line-Index/issues/67) |
| FDOCS-006 | [#68](https://github.com/pchemguy/Archive-Line-Index/issues/68) |
| FDOCS-007 | [#69](https://github.com/pchemguy/Archive-Line-Index/issues/69) |
| FDOCS-008 | [#70](https://github.com/pchemguy/Archive-Line-Index/issues/70) |
| FDOCS-009 | [#71](https://github.com/pchemguy/Archive-Line-Index/issues/71) |

## Decisions

| Decision | Source and state | Basis / consequence |
| --- | --- | --- |
| Standard logging; lightweight cumulative bytes; no per-line messages | Human request, confirmed. | Use ordinary named loggers, levels and handlers; no custom progress framework. |
| Five-second progress intervals | Human follow-up, confirmed. | Observe the interval at chunk boundaries; no background heartbeat. |
| Uncompressed indexed bytes using scanner position | Agent proposal, pending brief acceptance. | Existing scanner byte position covers plain/archive/direct-reader indexing without adapter-specific compressed counters. |
| CLI INFO on stderr with suppression; library configuration remains caller-owned | Agent proposal, pending brief acceptance. | Keeps stdout summaries while making normal CLI work observable; default success stderr intentionally gains progress. |
| Minimal indexing scope and unchanged signatures/storage/cleanup | Agent proposal, pending brief acceptance. | Standalone stream-only reads and per-row persistence progress remain outside the proposed first feature. |

## Stage evidence

| Stage | Source/applicability and decision/QC evidence |
| --- | --- |
| FDOCS-001 | Baseline/main/origin are aligned, worktree was clean, global sequence discovery across local/remote branches/review/feature/nested paths found maximum 005, and no active feature sources occupied these paths. All nine tracking identities and membership were read back before writes. Main accepted inputs and current scanner/CLI were inspected; scanner already tracks uncompressed position, while CLI currently promises quiet successful stderr and no progress UI. Context and task/control/HANDOFF records are coherent. Initialization commit 2273ec25cd9c9428dc038fb759b1c0db1e51df21 was published/read back; issue #63 was closed as completed and read back with its exact source evidence. |
| FDOCS-002 | Pass 1 proposal [FEATURE](FEATURE.md), content blob f49370835deb61b457bbbec2c41c9a6dae5761b7. Seed-coverage QC passes: standard logging, five-second cadence, cumulative bytes, no per-line work and light chunk-level cost are explicit. Retained index/resource/publication semantics and the proposed CLI stderr change are distinguished. All links/heading separation and source scope checks pass. First human approval remains pending; the checkbox and issue #64 stay open. |
| FDOCS-003–009 | Not started; preserve ordered dependencies and required later assessment/QC/approval. |

Manual provenance setup is reused without recording or altering conversations. Integrated docs/ai-logs/AGENTS.md is present; the original EXPLORE_DRIVE_TEMPLATE was deliberately renamed into the manual EXPLORE_DRIVE record in integrated commit 0b86c44. The existing published design-docs/ai-logs tip is already contained in main. This established setup is not missing bootstrap; preserve its deliberate rename and historical contents rather than recreate files or replay root initialization.

## Pending transitions

Publish/read back this FEATURE proposal on design-docs/006_c33ec54-progress-logging, present its intended behavior and material proposals, then hold for human acceptance. The five-second cadence is confirmed; uncompressed counting, default CLI INFO/stderr with level control and indexing-only coverage remain proposed brief content. FDOCS-002/#64 is not complete until actual acceptance is recorded and published with its initial checkoff. Later FDOCS issues and the preparation milestone remain open. No dependent architecture/specification, implementation, merge, version bump or release proceeds from a draft alone.
