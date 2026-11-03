# Project handoff

Checkpoint: milestone 1.2 verified by T-009 on `phase/1-plain-file-library`; publication/issue/milestone effects after this containing commit require readback. Later Git commits and TASKS checkoffs reconstruct continuation without repeating completed work.

## Scope and control

The human authorized T-001 through T-014 and explicitly requires stopping BEFORE T-015. Implement remaining selected tasks in order; no phase review, main integration, tag or release is authorized at this partial-phase boundary. Each completed verified integrated phase still requires a GitHub release with native versioned source/wheel assets, notes and checksums. CLI/persistence remain Phase 2; archives remain later phases. Do not hard-wrap Markdown.

Accepted PROJECT/ARCHITECTURE/DECOMPOSITION/SPEC/PLAN/layout/TASKS and their linked children govern the implementation. Preparation was integrated/published on main at `9c90eebc8aaca66f8f086cb69f93f0dbb7c571ee`; documentation milestone #1 and issues #1–9 are closed. The phase branch was created from that parent. Preserve design-docs/main and the separate manual-provenance branch.

## Verified capability and evidence

T-001–T-008 are committed, pushed and closed as issues #10–17. Milestone #2 is closed (six completed issues). T-009 completes canonical offset validation and bounded LF/BOM scanning, with its folded review/report/checkoff in this commit; see [milestone 1.2](reports/phases/1/1.2.md) and retained [milestone 1.1](reports/phases/1/1.1.md). Regression suite: 198 tests, 99% coverage, scanner 100%; Ruff lint/format and strict mypy pass. A 32 MiB generated single line stays below 128 KiB traced scanner memory with 8 KiB reads. No public facade/installed runtime claim yet.

Use the selected Python environment for pyproject-owned checks. On this Linux container mypy 2.4.1 needs `--no-native-parser` because its native parser's process discovery fails; strict checks pass with that supported fallback. Runtime/dev tools are isolated outside the repository. Root AGENTS remains the operational entry; pyproject owns configuration.

## Tracking and next action

Phase label: `sdd-phase-1-Plain-file-library`. Native milestones #2/#3/#4/#5 map to 1.1/1.2/1.3/1.4; task issues #10–24 map to T-001–T-015. All initial associations were read back before code work. T-015 issue #24 is projected only and must remain open/unstarted.

Publish/read back this task commit, close/read back issue #18, then verify milestone #3's three members closed/completed before closing/readback of milestone #3. If these effects already occurred, reuse them. Continue T-010–T-014; the next automatic report/HANDOFF is T-014. Stop after verified T-014 and milestone #4 closure on the phase branch without merging or releasing.
