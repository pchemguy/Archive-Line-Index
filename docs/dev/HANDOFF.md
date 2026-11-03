# Project handoff

Checkpoint: completed documentation package QC (DOCS-009), with final publication/integration/milestone transitions requiring actual readback. This snapshot is identified by its containing commit; recover subsequent effects from Git and provider state before continuing.

Outcome: the complete design/contract/PLAN/layout/TASKS suite is accepted and whole-package document QC passes after editorial-state corrections. It describes intended functionality and a 52-task implementation route; no product implementation or runtime verification is claimed.

## Workflow and sources

- Workflow/stage/owner: main preparation, interactive/onepass; sdd-manage owns final integration/closure and the implementation handoff.
- Governing entry points: [PROJECT](PROJECT.md), [ARCHITECTURE](ARCHITECTURE.md), [DECOMPOSITION](DECOMPOSITION.md), [SPEC](SPEC.md), [PLAN](PLAN.md), [layout](layout.md) and [TASKS](TASKS.md), including their linked children.
- Evidence and current control: [DOCS_TASKS](DOCS_TASKS.md), [DOCS_PREPARATION](DOCS_PREPARATION.md), [DOCS-QC-REPORT](DOCS-QC-REPORT.md) and the SPEC/PLAN/TASKS review reports.
- Available workflow guidance: installed and repository-vendored SDD Manager 0.16.1, root AGENTS and current pyproject tooling. No product source/test/build environment has been established.

## Scope and human decisions

- Authorized scope: complete documentation preparation and verified default-branch integration. Human acceptance covers all roots and selected design/contract/layout children; TASKS was accepted on 2026-11-03.
- Standing delivery policy: four phases, with a version tag/GitHub release after each verified/integrated phase, release notes and explicit source-distribution/wheel assets plus checksums/readback. CLI indexes one target once into both SQLite/raw outputs under the accepted input-directory/stem defaults.
- Exact stop: after verified preparation integration and documentation milestone closure, ask the human for an implementation range. No product phase/task is active and no implementation checkpoint is preapproved.
- Reporting/format: concise operational updates, substantive checkpoints and unwrapped Markdown unless explicitly requested. The temporary legacy reference in AGENTS remains until reimplementation closure.

## Branches and return

- Preparation branch: design-docs/main; creation parent and integration target: main.
- Original branch-off commit: c6398d8e51c60cabddc21997188e0a9cc040272d.
- Known prior acceptance checkpoint: 9d3bdde8cff48427e0a624b50292e7a81d7c34ef (TASKS acceptance); the containing DOCS-009 checkpoint adds whole-package evidence and bounded editorial repairs.
- Suspended parent workflow: none. Preserve the separate manual provenance branch and records; they are not continuation work.

## Pending effects and next action

- Verify the DOCS-009 completion commit is published and issue #9 is closed before integration; DOCS-001–008 closures were independently verified.
- Refresh the actual default branch, explicitly merge only the complete verified preparation, check the two parents and unchanged scoped source, then publish/read back main. Close/read back sdd-docs-main only after that published integration.
- If these transitions have already completed, reuse their observed identities rather than replay them. Return on the default branch and pause for the selected implementation range; eligible-phase activation and execution belong to that later handoff.
