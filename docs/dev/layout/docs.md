# Documentation and evidence ownership

## Product documentation and contracts

| Location | Canonical ownership |
| --- | --- |
| Root `README.md` | Installation, quick library/CLI use, delivered capability scope and discoverable project documentation links. |
| Root `RELEASE-NOTES.md` | Finalized notes for the release being prepared; published GitHub releases and Git history retain earlier versions. |
| `docs/dev/PROJECT.md` | Purpose, users, complete scope/non-goals and consequential constraints. |
| `docs/dev/ARCHITECTURE.md` | Major system blocks, dependencies and structural rationale. |
| `docs/dev/DECOMPOSITION.md` and `decomposition/` | Logical component/model ownership and canonical public/internal API design. |
| `docs/dev/SPEC.md` and `spec/` | Complete behavior, detailed contracts and acceptance conditions, including the CLI and independent persistence. |
| `docs/dev/PLAN.md` | Phase/milestone outcomes, delivery dependencies, review/integration gates and per-phase release policy. |
| `docs/dev/layout.md` and `layout/` | Physical source/test/document/build ownership, without duplicated contracts or task status. |
| Python module/API docstrings | Professional documentation beside the implementation; they describe supported behavior without becoming a competing normative specification. |

Product documents describe the system directly and contain no migration history. Root README and module docstrings provide user guidance; accepted design/contracts remain linked owners rather than copied material. Markdown prose/list items are single source lines unless the human explicitly requests wrapping; literal code/diagram structure is preserved.

## Workflow records and review evidence

`docs/dev/DOCS_TASKS.md` owns only preparation definitions/checkoffs, `DOCS_PREPARATION.md` owns decisions/identities/current transitions, and `HANDOFF.md` owns periodic continuity checkpoints. `TASKS.md` owns the intended executable hierarchy once derived; it is not duplicated in layout or reports. These workflow records are distinct from product scope/contracts.

`SPEC-REVIEW-REPORT.md`, `PLAN-REVIEW-REPORT.md` and `TASKS-REVIEW-REPORT.md` sit beside their governing roots. PLAN review covers the root and every selected layout child. `DOCS-QC-REPORT.md` owns the eventual whole-preparation assessment. Reports retain exact reviewed identities, findings and rechecks rather than claiming runtime evidence from document readiness.

Implementation milestone reports belong under `docs/dev/reports/phases/<phase-id>/<milestone-id>.md`; phase reports use `PHASE-REPORT.md` in the phase directory; the final report is `docs/dev/reports/IMPLEMENTATION-REPORT.md`. Assigned boundary tasks own their evidence and checkpoint updates under the existing workflow. Release results link the exact source/tag/artifacts and hosted-byte verification from the owning phase/release evidence.

`docs/ai-logs/` retains its own historical-record instructions and is outside routine orientation, product validation and distribution inventory. `.agents/` contains vendored development capabilities with separate ownership; it is not production package code or a source of product requirements. Root disclosures, discovery instructions and AGENTS retain their established roles without embedding duplicated task lists or transient branch snapshots.
