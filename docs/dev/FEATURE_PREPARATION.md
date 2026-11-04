# Feature preparation record

## Identity and request

Campaign 006_c33ec54; descriptive association 006_c33ec54-progress-logging. Full starting baseline and recorded creation parent main: c33ec544e06134ab71866a4bf2f46ad21c9d150d. Actual preparation branch design-docs/006_c33ec54-progress-logging; default preparation/integration target main. Intended later implementation parent main containing the verified preparation merge; intended implementation branch feature/006_c33ec54-progress-logging, not yet created. Reserve docs/dev/features/006_c33ec54-progress-logging/ for eligible future reports/archive; active feature sources belong in docs/dev, without a placeholder navigation package.

The human requested opening a feature campaign for minimal lightweight progress on large sources, cumulative uncompressed or compressed bytes using whichever needs less new code, no per-line progress, proper standard Python logging. The follow-up confirms five-second increments. The later human acceptance “k. Use autodoc with preapproved QC and full implement checkpoints” accepts the presented FEATURE and authorizes the remaining preparation, package QC and full feature implementation without repeated approval pauses. Retain baseline 0.4.1 functionality, frozen campaigns 001–005, original task/hosted closures and releases.

Active sources: [feature documentation tasks](FEATURE_DOCS_TASKS.md), this record and [HANDOFF](HANDOFF.md). [FEATURE](FEATURE.md) is now the published-for-review proposal; its first approval is accepted by the latest human instruction. Affected main context is PROJECT, ARCHITECTURE, DECOMPOSITION and public API design, SPEC's line-index/public-operation/CLI contracts, PLAN/layout, scanner/api/cli and their tests. These are current reference inputs, not amended by opening.

## Current control

Autodoc/onepass, pass 1, strict delivery. The human accepted FEATURE blob f49370835deb61b457bbbec2c41c9a6dae5761b7 and preapproved subsequent document, whole-package QC and full implementation checkpoints. This explicit advance overrides autodoc's ordinary FDOCS-008 stop. Complete scoped design/spec/plan/layout/tasks and QC, verify/publish preparation integration and tracking closure, execute the full accepted feature task range, incorporate/verify/integrate and publish its phase release under the retained project release policy. QC, task-level publication and hosted gates remain mandatory. No unrelated feature or deferred cleanup is selected.

Root AGENTS enables GitHub tracking throughout documentation/implementation by default. The pre-write gate is verified before this branch/ref and repository writes: [milestone #16](https://github.com/pchemguy/Archive-Line-Index/milestone/16) is open and all nine campaign-qualified stage issues have matching titles, opening/closing task markers, feature-scope marker and native milestone association. Their complete briefs came from the pinned bundled FEATURE_DOCS_TASKS_TEMPLATE, not product task-list inference.

| Stage | Hosted issue |
| --- | --- |
| FDOCS-001 | [#63](https://github.com/pchemguy/Archive-Line-Index/issues/63) |
| FDOCS-002 | [#64](https://github.com/pchemguy/Archive-Line-Index/issues/64) |
| FDOCS-003 | Assessed ARCHITECTURE against accepted FEATURE: existing scanner byte-position ownership, downward CLI composition and independent persistence remain sufficient. Logging is standard-library observation, not a new data plane, worker or component dependency. No FEATURE_ARCHITECTURE overlay is needed; preserve resource and format boundaries. FDOCS-002 checkpoint 02efc2a4976420f316364dad7c52356ca4803398 is published/hosted-closed. Accepted under the human autodoc/QC/full-implementation preapproval. Publish/read back this containing stage before hosted closure or advancement. |
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
| Uncompressed indexed bytes using scanner position | Accepted by FEATURE approval; exact technical details delegated to normal scoped design. | Existing scanner byte position covers plain/archive/direct-reader indexing without adapter-specific compressed counters. |
| CLI INFO on stderr with suppression; library configuration remains caller-owned | Accepted by FEATURE approval; exact technical details delegated to normal scoped design. | Keeps stdout summaries while making normal CLI work observable; default success stderr intentionally gains progress. |
| Minimal indexing scope and unchanged signatures/storage/cleanup | Accepted by FEATURE approval; exact technical details delegated to normal scoped design. | Standalone stream-only reads and per-row persistence progress remain outside the proposed first feature. |

## Stage evidence

| Stage | Source/applicability and decision/QC evidence |
| --- | --- |
| FDOCS-001 | Baseline/main/origin are aligned, worktree was clean, global sequence discovery across local/remote branches/review/feature/nested paths found maximum 005, and no active feature sources occupied these paths. All nine tracking identities and membership were read back before writes. Main accepted inputs and current scanner/CLI were inspected; scanner already tracks uncompressed position, while CLI currently promises quiet successful stderr and no progress UI. Context and task/control/HANDOFF records are coherent. Initialization commit 2273ec25cd9c9428dc038fb759b1c0db1e51df21 was published/read back; issue #63 was closed as completed and read back with its exact source evidence. |
| FDOCS-002 | Pass 1 proposal [FEATURE](FEATURE.md), content blob f49370835deb61b457bbbec2c41c9a6dae5761b7. Seed-coverage QC passes: standard logging, five-second cadence, cumulative bytes, no per-line work and light chunk-level cost are explicit. Retained index/resource/publication semantics and the proposed CLI stderr change are distinguished. All links/heading separation and source scope checks pass. Accepted by the subsequent human “k” and autodoc/QC/full-implementation preapproval; this checkpoint records the initial FDOCS-002 completion, with publication then #64 closure pending. |
| FDOCS-003 | Assessed ARCHITECTURE against accepted FEATURE: existing scanner byte-position ownership, downward CLI composition and independent persistence remain sufficient. Logging is standard-library observation, not a new data plane, worker or component dependency. No FEATURE_ARCHITECTURE overlay is needed; preserve resource and format boundaries. FDOCS-002 checkpoint 02efc2a4976420f316364dad7c52356ca4803398 is published/hosted-closed. Accepted under the human autodoc/QC/full-implementation preapproval. Publish/read back this containing stage before hosted closure or advancement. |
| FDOCS-004 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |
| FDOCS-005 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |
| FDOCS-006 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |
| FDOCS-007 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |
| FDOCS-008 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |
| FDOCS-009 | Pending; applicable acceptance is preapproved, technical QC and ordered publication/hosted closure remain required. |

Manual provenance setup is reused without recording or altering conversations. Integrated docs/ai-logs/AGENTS.md is present; the original EXPLORE_DRIVE_TEMPLATE was deliberately renamed into the manual EXPLORE_DRIVE record in integrated commit 0b86c44. The existing published design-docs/ai-logs tip is already contained in main. This established setup is not missing bootstrap; preserve its deliberate rename and historical contents rather than recreate files or replay root initialization.

## Pending transitions

Publish/read back this accepted FEATURE/mode checkpoint and close/read back #64, then continue FDOCS-003–009 under preapproval. No additional human pause is needed at the autodoc pass stop, package QC or full implementation checkpoint. Preserve five-second chunk-boundary cadence, light operation and caller logging ownership; resolve only material scope changes outside the accepted brief with the human.
