# Main documentation preparation record

## Current control

- Mode and decision source: interactive/onepass, explicitly requested by the human.
- Current pass and scope: onepass; new design and implementation of Archive Line Index informed by the legacy repository.
- Approval basis: each necessary document checkpoint remains active. No future document approval or implementation range is preapproved.
- Tracking/publication selection: root AGENTS enables documentation and implementation tracking by default; the human explicitly requested creation of the documentation milestone and nine issues on 2026-11-03. Publish/read back each owned commit.
- Next boundary: publish SPEC, its five contract children and SPEC-REVIEW-REPORT; pause for human acceptance before PLAN.

## Scope and decisions

The human requested a new design suite and subsequent implementation in `pchemguy/Archive-Line-Index`, using legacy material from `pchemguy/Archive-Line-Index-Legacy` as adaptable input. This is main preparation, not a transfer of legacy completion status. Scope/functionality/decisions may be retained where appropriate; proposal content requires the current checkpoints. The immediate outputs are root AGENTS tooling guidance and the project brief.

The new repository baseline is `c6398d8e51c60cabddc21997188e0a9cc040272d`; the inspected legacy baseline is `5eacaddd46dcd6ac064bd082a2bde456c57f33a6`. Read-only inspection covered the legacy README, architecture, root SPEC and relevant public-API, archive, stream, line-index and persistence contracts; the new pyproject owns tooling inputs. Historical logs were excluded.

## Decisions and document evidence

| Task | Current evidence / decision basis |
| --- | --- |
| DOCS-001 | All four root guidance/disclosure/discovery files retained byte for byte in initialization; task/control/HANDOFF records created from SDD Manager 0.16.1 guidance. Pre-write projection and preservation checks verified before initialization; milestone `sdd-docs-main` #1 and DOCS-001–009 issues #1–9 have exact predefined content and verified associations. |
| DOCS-002 | PROJECT SHA-256 `b2c2e55722e5bd68aef98b0dd82ef1116d71826730edc2ad98a1f4a9fe482b85`, published unchanged since commit `68457f1c5e51a5899bd5868ca464c41c11d9d7d2`, accepted by the human on 2026-11-03: “PROJECT is ok”. Brief consistency and formatting checks passed. DOCS-002 completion published in `97a692c83208d8abd876ad74b74074a66f78bed9`; issue #2 closed with evidence and independent readback. |
| DOCS-003 | ARCHITECTURE SHA-256 `08a65b86da46847a99bea949590c0b04f614f86acf52e9942e1c86762e773b67`, proposed in `1d30f5a05ab9b23e8f41b24e44cd2aafe7ca0779`, accepted by the human on 2026-11-03 (“k” in direct response to its acceptance checkpoint). Consistency, ownership, dependency, lifecycle and Markdown checks passed. DOCS-003 completion published in `71767dbc8f5b66c83102d52bee6712dbd8e8ad3a`; issue #3 closed with evidence and independent readback. |
| DOCS-004 | Proposal set: `docs/dev/DECOMPOSITION.md` SHA-256 `bbbacb93ea0e07b28c95690322b89c1ebe07c07079a20709649adb2d384a9fda`; `docs/dev/decomposition/public-api.md` SHA-256 `bb9fa69aeb8c90594e574dd7a7966c31056a6b899bdcb890290182e91df832ef`; `docs/dev/decomposition/internal-api.md` SHA-256 `be853e14b93d5129c59419eabe64e9b44291f1df76a6b9656891faf234b08a61`. The root owns components and the offset model; public/internal API children own their declarations and lifecycle/message definitions. Reviewed together against accepted ARCHITECTURE. Accepted by the human on 2026-11-03 (“k” in direct response to the complete decomposition-set checkpoint). Approved bytes retained from proposal commit `e50bd418dfbe4a50b1b1df10318f0f187072c06c`; DOCS-004 checked with this decision record. Completion published in `f2630445eafd76ead0b9be44e780c0274b25f873`; issue #4 closed with evidence and independent readback. |
| DOCS-005 | SPEC and its five contracts are proposed; exact reviewed/governing identities, two corrected findings and the Ready design-conformance assessment are in [SPEC-REVIEW-REPORT](SPEC-REVIEW-REPORT.md). The public/internal API and model definitions remain owned by the accepted decomposition set. Human acceptance pending; task unchecked and issue open. |
| DOCS-006–009 | Pending their prerequisites and interactive checkpoints. |

## Initialization

- Original root-file presence: all four existed; AI_DISCLOSURE.md, SDD-MANAGER.md, AGENTS.md and SKILL_DISCOVERY_PROTOCOL.md retained. No root template copied or reconciled during DOCS-001.
- Preservation verification: SHA-256 comparison against the pinned initial tree; all four unchanged in initialization.
- Initialization continuation: all present; no mixed-presence stop.
- Manual provenance setup: default enabled and already present in main from initial commit `28fe361a56171dd0607d599082ac6f8553f9a20b`. Both scaffold files are tracked and valid; no new scaffold seed/merge was necessary. Existing later manual changes on design-docs/ai-logs are not part of this operation and were not read or merged.
- Current reset: none.
- Tooling observation: Linux execution host, Python 3.12.14, Node 24.22.1, Git 2.51.1. Source/tests and README absent at initialization; pyproject parses but lacks a static or dynamic version. Declared Python development tools were absent in the inspected interpreter. Product checks have not run.

## Pending transitions

Initialization commit `79975f0b67ec5a086a69de5f69f1dd143853f564` was pushed and its exact remote ref verified; DOCS-001 issue #1 is closed as completed with evidence and independent readback. PROJECT acceptance checkpoint `97a692c83208d8abd876ad74b74074a66f78bed9` is published with exact remote readback; DOCS-002 issue #2 is closed as completed with evidence and independent readback. ARCHITECTURE acceptance checkpoint `71767dbc8f5b66c83102d52bee6712dbd8e8ad3a` is published with exact remote readback; DOCS-003 issue #3 is closed as completed with evidence and independent readback. Decomposition acceptance checkpoint `f2630445eafd76ead0b9be44e780c0274b25f873` is published with exact remote readback; DOCS-004 issue #4 is closed as completed with evidence and independent readback. Publish/read back the specification proposal and adjacent review report, then await human acceptance. DOCS-005 remains unchecked and issue #5 open. No implementation range is selected.


## Proposal assessment

The PROJECT proposal retains the two independent capabilities, byte fidelity, archive validation, LF/BOM/EOF semantics, bounded payload buffering, explicit resource ownership and independent validated persistence. Its intended platforms and exclusions come from the legacy scope, rather than from demonstrated new implementation. Architecture, detailed interfaces and contracts remain open for their own design checkpoints; legacy source/test layout and test-pass claims have not been adopted.

Root AGENTS project guidance was updated after DOCS-001 preservation, under the human's explicit request. Commands are derived from pyproject and labeled as intended rather than validated: no source/tests or declared development tools were available. Missing version metadata is recorded for later packaging work; pyproject itself is unchanged. README now provides truthful status and links.

Checks: TOML parsed successfully; existing AGENTS policy prefix preserved; project brief assessed against the inspected inputs; authored Markdown headings, indentation, links and credential exclusion checked; git diff whitespace check passed. No product tests, lint/type checks, distribution build or native-platform verification ran. No dependencies were installed.

## Guidance correction and closure obligation

The human requested concise operational project guidance, preserving AGENTS.md's single-line prose style and removing configuration restatement, repeated instruction-discovery guidance and transient verification commentary. The legacy reference is temporary and must be removed at reimplementation closure. Product documents must contain no migration narrative or history. PROJECT is accepted; later document checkpoints remain interactive.

The human requested removal of hard wrapping from PROJECT. Only whitespace changed; wording, headings and list membership were preserved. Root guidance now applies the no-hard-wrap rule to Markdown prose and list items. PROJECT is accepted; later document checkpoints remain interactive.

## Architecture proposal assessment

ARCHITECTURE assigns content access, stream behavior, scanning, offset validation and persistence to distinct owners with directed dependencies. It proposes a bounded queue/extraction-thread bridge for 7z, explicitly distinguishes cooperative cancellation from fixed-time termination, and identifies dependency suitability checks. Persistence separates protected creation from replacement and requires explicit filesystem failure semantics in SPEC. No public signatures, physical module tree or implementation task sequence is defined at this stage. The proposal contains no migration narrative and uses unwrapped Markdown prose. Review covered accepted scope, cohesion, dependency direction, ownership, completion semantics, resource accounting and navigation. ARCHITECTURE is accepted; no implementation verification is claimed.

## Decomposition proposal assessment

The proposal assigns every public and internal collaboration to a provider and consumer, with explicit ownership transfer for backend readers, borrowed streams, 7z archive/thread state and temporary paths. It selects two focused API children under the same DOCS-004 checkpoint; the root remains the canonical offset-model owner. The public scanner accepts a minimal readable protocol rather than requiring unrelated BinaryIO capabilities. The publication interface separates the publication commit point from later temporary cleanup. Review checked accepted scope, dependency direction, interface coverage, resource/state ownership, model consistency, verification seams, links and unwrapped Markdown prose. Exact behavioral contracts and acceptance remain for SPEC; no source code, tests or physical layout have been created.

## Specification proposal assessment

The complete contract set is SPEC plus spec/public-api.md, content-stream.md, archive-handling.md, line-index.md and persistence.md. SPEC-REVIEW-REPORT retains exact identities, grouped design coverage and the correction/recheck evidence for argument-rejection state and standalone SQLite publication. The set defines supported format/filter scope, read/EOF/failure precedence, finite buffering, canonical line examples, protected publication and post-publication cleanup outcomes. All source text is unwrapped except semantic code/diagram structure. Technical document readiness is Ready; the human acceptance checkpoint remains active. No implementation, PLAN authoring or task-range selection has started.
