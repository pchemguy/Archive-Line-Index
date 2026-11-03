# Main documentation preparation record

## Current control

- Mode and decision source: interactive/onepass, explicitly requested by the human.
- Current pass and scope: onepass; new design and implementation of Archive Line Index informed by the legacy repository.
- Approval basis: each necessary document checkpoint remains active. No future document approval or implementation range is preapproved.
- Tracking/publication selection: root AGENTS enables documentation and implementation tracking by default; the human explicitly requested creation of the documentation milestone and nine issues on 2026-11-03. Publish/read back each owned commit.
- Next boundary: prepare and publish PROJECT, then pause for human acceptance before ARCHITECTURE.

## Scope and decisions

The human requested a new design suite and subsequent implementation in
`pchemguy/Archive-Line-Index`, using legacy material from
`pchemguy/Archive-Line-Index-Legacy` as adaptable input. This is main preparation,
not a transfer of legacy completion status. Scope/functionality/decisions may be
retained where appropriate; proposal content requires the current checkpoints.
The immediate outputs are root AGENTS tooling guidance and the project brief.

The new repository baseline is
`c6398d8e51c60cabddc21997188e0a9cc040272d`; the inspected legacy baseline is
`5eacaddd46dcd6ac064bd082a2bde456c57f33a6`. Read-only inspection covered the legacy
README, architecture, root SPEC and relevant public-API, archive, stream,
line-index and persistence contracts; the new pyproject owns tooling inputs.
Historical logs were excluded.

## Decisions and document evidence

| Task | Current evidence / decision basis |
| --- | --- |
| DOCS-001 | All four root guidance/disclosure/discovery files retained byte for byte in initialization; task/control/HANDOFF records created from SDD Manager 0.16.1 guidance. Pre-write projection and preservation checks verified before initialization; milestone `sdd-docs-main` #1 and DOCS-001–009 issues #1–9 have exact predefined content and verified associations. |
| DOCS-002 | PROJECT proposal pending; no human acceptance. |
| DOCS-003–009 | Pending their prerequisites and interactive checkpoints. |

## Initialization

- Original root-file presence: all four existed; AI_DISCLOSURE.md, SDD-MANAGER.md, AGENTS.md and SKILL_DISCOVERY_PROTOCOL.md retained. No root template copied or reconciled during DOCS-001.
- Preservation verification: SHA-256 comparison against the pinned initial tree; all four unchanged in initialization.
- Initialization continuation: all present; no mixed-presence stop.
- Manual provenance setup: default enabled and already present in main from initial commit `28fe361a56171dd0607d599082ac6f8553f9a20b`. Both scaffold files are tracked and valid; no new scaffold seed/merge was necessary. Existing later manual changes on design-docs/ai-logs are not part of this operation and were not read or merged.
- Current reset: none.
- Tooling observation: Linux execution host, Python 3.12.14, Node 24.22.1, Git 2.51.1. Source/tests and README absent at initialization; pyproject parses but lacks a static or dynamic version. Declared Python development tools were absent in the inspected interpreter. Product checks have not run.

## Pending transitions

Publish/read back initialization and close/read back DOCS-001 before dependent
PROJECT work. No document is accepted and no implementation is authorized yet.
