# Project handoff

Checkpoint: Phase 1 is finalized, integrated on main and released as [v0.1.0](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.1.0). This containing report commit records verified external effects; publish/read back it if still pending, then stop.

## Current outcome and boundary

T-001–T-015 and all Phase 1 milestones are complete. The human authorized Phase 1 finalization; Phase 2 has not been selected. Do not activate or execute T-016 or later without a new instruction. All Phase 1 task issues #10–24 and native milestones #2–5 are closed/completed. Accepted design/contracts/PLAN/layout/TASKS retain their ownership; TASKS contains the executable checkoffs. Markdown prose/list items remain unwrapped.

The 0.1.0 library provides owned plain-file binary streaming, generic borrowed-reader LF/BOM scanning, canonical Q/eight-byte offsets and source-based index building, with validation, inclusive limits and cleanup/failure guarantees. Typed exports, native packaging/inventory checks and executable README purpose/input/output/interface examples are delivered. Product CLI/persistence and archive adapters remain later-phase work. The temporary legacy reference in AGENTS remains until full reimplementation closure.

## Git and release identities

- Phase branch: `phase/1-plain-file-library`, preserved at published T-015 `0fa719b0b08de33cee1124627cf59077230a21a3`.
- Creation parent: accepted preparation main `9c90eebc8aaca66f8f086cb69f93f0dbb7c571ee`.
- Published explicit two-parent integration: `f1365f0457a616917628c8b2a0c8d9bb72b64f14`.
- Published main release commit and `v0.1.0` target: `2d0435cc731d608843ad71cfa9c7688d1d8b5d09`.
- GitHub release ID 432848257: published, non-prerelease, verified latest. The later evidence commit leaves the tag/source unchanged. Preserve design and manual-provenance branches.

## Verification and evidence

[Phase report](reports/phases/1/PHASE-REPORT.md) records review, acceptance mapping, task composition, integration and full release asset URLs/sizes/hashes. The source distribution, wheel and SHA256SUMS were built from the exact release commit, uploaded and then downloaded with matching bytes. Release commit body, root RELEASE-NOTES.md and hosted body match exactly. Both native and independently source-rebuilt wheels pass installed workflows and all three README examples in clean runtimes outside checkout; runtime py7zr 1.1.4 was recorded. No dev tools or source-path injection are required for installed use.

Phase source checks: 253 tests, 99% production coverage, Ruff lint/format and strict mypy pass; merged-state suite also passes. Linux/bash and CPython 3.12.14 were used. Mypy requires its supported `--no-native-parser` fallback for this container's native process-discovery failure. Native Windows/macOS/Python 3.11 runtime checks and archive dependency behavior remain unverified. Root AGENTS/pyproject provide operational instructions/configuration.

The final notes file remains tracked. Only the workflow-owned ignored highlights draft is removed after exact published-body verification. Pending effects for this containing evidence commit are its main publication/readback; no release retry is needed. Once published, return the completed Phase 1 result and pause before Phase 2.
