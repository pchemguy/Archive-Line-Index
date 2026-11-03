# Project handoff

Checkpoint: verified documentation integration on main; target publication and documentation-milestone closure require actual readback after this merge commit. This snapshot is identified by its containing commit; recover subsequent effects from Git and provider state before continuing.

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

- Current receiving branch: main. Preparation branch: design-docs/main; creation parent and integration target: main.
- Original branch-off commit: c6398d8e51c60cabddc21997188e0a9cc040272d.
- Pinned integration parents: main `c6398d8e51c60cabddc21997188e0a9cc040272d` and preparation `33c582df1ed181b5ae38fcbc0663af57362fc35d`. The latter is the published passing DOCS-009 checkpoint; its issue #9 closure is independently verified.
- Suspended parent workflow: none. Preserve the separate manual provenance branch and records; they are not continuation work.

## Pending effects and next action

- All nine DOCS issues are closed with verified evidence. The prospective merged tree passed package/hash/link/structure checks; no product requirements, tasks or implementation changed during integration.
- Finish/verify the containing explicit two-parent integration commit, publish/read back main, then close/read back sdd-docs-main. These external effects occur after this checkpoint and must be reconciled from actual state.
- If these transitions have already completed, reuse their observed identities rather than replay them. Return on the default branch and pause for the selected implementation range; eligible-phase activation and execution belong to that later handoff.

## Active implementation selection

The human authorized T-001 through T-014, stopping before T-015. Preparation main commit `9c90eebc8aaca66f8f086cb69f93f0dbb7c571ee` and documentation milestone #1 closure were verified before branching to `phase/1-plain-file-library`. Phase activation verified label `sdd-phase-1-Plain-file-library`, native milestones #2–5 and task issues #10–24 (T-001–T-015 respectively). T-015 is projected only and remains unstarted. The selected partial phase must remain unmerged and unreleased. Later task commits and checkoffs supersede the earlier preparation-only snapshot above; boundary tasks refresh this handoff.
