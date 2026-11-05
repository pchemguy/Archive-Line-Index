# README and documentation revision plan

## Campaign and authority

Campaign 008_af8ae75; working branch revision/008_af8ae75-readme-docs; creation parent and intended integration target main; full branch-off baseline af8ae75219275e0142f4abdcb09bb10443f1fda6. The user requested opening a README/docs revision campaign. State: V-001–V-008 executed and verified; D-001 resolved as Integration contract. Campaign remains Open pending further human direction; integration/closure/release are not selected.

## Scope and boundaries

The campaign concerns README.md and maintained project documentation: overview, inputs/outputs, public interfaces, usage examples, installation, progress logging, navigation and consistency with supported behavior. Specific revision actions and their verification will be recorded when selected. No defect, review result, accepted amendment or completed change is implied by campaign opening.

At opening, authorization covered this campaign's branch, opening records, HANDOFF and publication, stopping before review or product-document edits. Subsequent scoped amendments and review authorization are retained below; the current request authorizes revision planning and publication only. Preserve all closed campaign/feature records and existing tags/releases. Runtime changes, governing requirement amendments, version bumps, release publication and integration are not selected by this opening request. Retain Markdown paragraphs and list items on single source lines.

## Evidence and continuation

[REVISION-REPORT.md](REVISION-REPORT.md) records actual campaign work. Future accepted revisions will receive stable action IDs, affected owners and objective checks. Preserve evidence and publish/read back each owned checkpoint before dependent work. No executable revision action or product task is allocated at opening.

## Accepted amendment — V-001

The user requested grouping different backends into one README section with subsections. V-001 introduces Source backends with Plain files, ZIP, TAR and 7z subsections, retaining all existing descriptions and examples. This later instruction authorizes this focused README edit and its campaign evidence/publication beyond the opening-only checkpoint; campaign closure, integration and release remain unselected. Verify heading hierarchy, unchanged non-heading content/code blocks, local links and diff whitespace; no production behavior or test changes are needed.

## Accepted amendment — V-002

The user requested consumer-oriented source-to-output guidance and confirmation that library/CLI consumers need no backend imports or explicit format selection. Add a README Consumer contract section covering the existing automatic source selection, library array/persistence workflow, CLI paired output and direct links to public API, CLI, index, persistence and input acceptance contracts. This documents delivered interfaces; it does not add a combined library operation or change requirements. Verify against public exports, API composition, detector/registry and current contracts; preserve all executable examples and validate local links. Campaign remains open after publication.

## Accepted clarification — V-003

Refine Consumer contract into a concise integration reference usable by people and agents implementing consumer software. Summarize public source-to-output interfaces and guarantees, then map integration concerns to authoritative specifications. Keep implementation detail and tutorial repetition outside this section; retain explicit distinction between library array/persistence and CLI paired output. Verify linked contract coverage, unchanged executable examples and Markdown/link structure. Publish and pause within the open campaign.

## Critical composition review authorization

The user subsequently requested critical composition review. Scope is the complete current README and its consumer-contract navigation, assessed against the stated audience and source-to-output intent. The review is findings-only; [REVIEW-REPORT.md](REVIEW-REPORT.md) owns its coverage, located findings, priorities, recommended sequence and evidence limits. This does not preauthorize the proposed repairs, closure, integration or release.

## Proposed composition revision

### Objective and current authority

The user requested a revision plan after the critical review and explicitly asked to include whether Consumer contract is the best title. The [review report](REVIEW-REPORT.md) pins the assessed README to af226cae5896df44054c60c313f6d85cd64ced0c; its published review checkpoint is caa543e22f6c8ff4ade098ae1120ce168cf7ec8e. This plan proposes remedies for R-001–R-006, preserving earlier verified V-001–V-003 work. Findings remain Open; planning neither fixes them nor authorizes execution, integration, closure or release.

The audience distinction is settled: software consumes archive-line-index; human developers and implementation agents use the documentation to implement that consuming software. The README should provide an accurate public-interface overview, a direct source-to-output path and a compact map to authoritative contracts, without requiring backend implementation knowledge.

### D-001 — Is Consumer contract the best section title?

Question: should Consumer contract remain, or should the section use a heading that more directly identifies its role as the integration boundary for software consuming the package through Python or CLI?

| Title | Strength | Limitation | Assessment |
| --- | --- | --- | --- |
| Consumer contract | Familiar terminology for a dependency's consumer-facing boundary; matches the user's initial working description. | Can be read as obligations imposed on the consumer or as a separately maintained formal contract, rather than a summary pointing to existing specifications. | Valid, but less immediately explicit for a general README reader. |
| Integration contract | Names the purpose: what consuming software may call, receive and rely on across library and CLI use. Fits an interface summary plus specification map. | Could still sound like a new normative specification unless the introductory sentence identifies the linked contracts as authoritative. | Recommended. |
| Public interfaces and contracts | Explicit about both public entry points and the linked references; covers Python and CLI without introducing consumer terminology. | Longer; can suggest an exhaustive API reference rather than a concise integration entry point. | Strong alternative if explicitness is preferred over a short heading. |

Recommendation: use Integration contract, with a brief introduction stating that this is the public integration summary and that the linked specifications define exact behavior. Retain the distinction between API signatures and operational/error semantics. This is a proposed editorial choice, not an accepted rename or a change to normative authority. D-001 is resolved when the title is selected as part of plan acceptance or later direction; execution must record that selection and update any maintained heading links.

### Proposed document structure and information ownership

| Order | Unit | Main responsibility |
| --- | --- | --- |
| 1 | Opening overview | Purpose, accepted input families, principal outputs and one small offset example; acknowledge independently usable streaming without repeating a full API table. |
| 2 | Installation | Supported Python/dependency prerequisites and direct installation; keep contributor packaging rationale with development instructions. |
| 3 | Integration contract, subject to D-001 | One compact summary of the two interfaces, Python library and CLI, plus the core specification map. Library persistence belongs within the library interface. |
| 4 | Library workflow | Supply an existing source, obtain offsets, optionally persist and reload them. Explain the array/file distinction and explicit destinations beside the example. |
| 5 | CLI workflow | Supply a source, obtain both output files; show console/module/imported forms with local naming, overwrite and status guidance. |
| 6 | Source backends | Parent-level shared path/detection/ownership and archive acceptance rules, then Plain files, ZIP, TAR and 7z subsections containing only relevant differences/setup examples. |
| 7 | Streaming and borrowed readers | Independent advanced public operations, ownership and bounded reads; do not interrupt the primary source-to-output workflow. |
| 8 | Progress and operational limits | Application logging setup, cadence, suppression, source failure and publication qualifications; group related memory/failure facts without hiding essential warnings from workflow sections. |
| 9 | Line-boundary scanning | Retain the requested bytes.find excerpt, alternatives, rationale and implementation link after the consumer workflows. |
| 10 | Development | Contributor checks, packaging/naming verification and development-document navigation. |

This outline assigns a main home rather than banning useful local reminders. Keep a concise independent-publication warning alongside operations that can partially publish. Preserve the user-approved single Source backends section with subsections. Add short task navigation only if it materially helps the retained structure; do not add a competing third interface inventory.

### Ordered actions

| Action | Findings / decision | Proposed changes and owners | Dependencies | Objective recheck |
| --- | --- | --- | --- | --- |
| V-004 | D-001; R-001, R-002, R-005 | Select the heading; reorganize README opening and integration summary around the two interfaces; preserve the core contract map and remove competing interface inventories. | Accepted execution scope and title selection. | Opening still states purpose/input/output; one main public integration map; Python construction/persistence and CLI are distinguishable; every core contract remains linked and heading links resolve. |
| V-005 | R-001, R-002 | Put complete library source-to-array/persistence and CLI source-to-pair workflows immediately after the integration reference. Place advanced streaming and the scanner implementation explanation later. | V-004 establishes structure. | A reader with an existing source can locate entry point, result, output paths and failure handling without traversing backend setup or scanner internals. Existing runnable workflow examples remain complete. |
| V-006 | R-003, R-004 | Lift common path/detection/facade rules to the Source backends parent. Keep format-specific restrictions in its four subsections. Explicitly separate archive-creation fixture setup from the common consuming call; retain self-contained examples where they add value. | V-005 avoids competing placement for the main build example. | Shared rules are discoverable without reading Plain files; no backend import/selection appears necessary for consumption; all format qualifications and runnable fixture setup remain accounted for. |
| V-007 | R-006; local density from R-005 | Place application logging setup with Progress logging; remove unrelated setup from the borrowed-reader example. Edit overloaded table/paragraph cells left after restructuring, preserving exact guarantees and terminology. | V-004–V-006 establish final homes. | Source-based callers find logging setup locally; borrowed-reader example teaches borrowing; application-owned logging, five-second updates and scan/publication distinction remain explicit. |
| V-008 | R-001–R-006 | Recheck full README composition and retained facts, execute affected installed examples, update active review dispositions and revision evidence, and report remaining issues. Coordinate any necessary example-inventory test adjustment with the docs change. | V-004–V-007 verified and published in order. | Each finding has located after-state evidence; links/anchors and Markdown structure pass; actual examples run against installed wheel and source-rebuilt packages; protected records/source/API/version remain unchanged. |

Actions are proposed, not complete. Preserve V-001–V-003 identifiers and evidence; do not invent executable product T tasks for this documentation maintenance. Commit each authorized action with its actual verification/report update, publish/read back before dependent work, and keep failed/unknown checks explicit. V-008 verifies the selected revisions; it does not itself authorize campaign closure, main integration or a release.

### Content-preservation and scope constraints

Retain automatic format selection, no consumer backend import requirement, plain/ZIP/TAR/7z support, the sole-regular-payload rule, original uncompressed byte coordinates, LF/BOM/EOF semantics, array versus persisted-file outcomes, explicit library destinations, public CLI callable, naming/overwrite/error statuses, independent publication and cleanup warnings, logging ownership/cadence, bounded storage and the explicitly requested scanner explanation. Preserve public identifiers, code meaning, qualifiers and exact file formats; do not strengthen guarantees while shortening prose.

The existing contract links are sufficient: decomposition/public-api.md, spec/public-api.md, spec/cli.md, spec/line-index.md, spec/persistence.md, spec/archive-handling.md and spec/progress-logging.md. Streaming details can retain their separate content-stream reference where needed. Do not merge specifications, write a new normative consumer spec or amend PROJECT/SPEC/PLAN merely to reorganize the README. If a true requirement conflict appears, report it separately for a decision.

No new guide/file is needed by default: first clarify and group existing examples in README. If moving substantial fixture material to a new examples guide becomes necessary, propose its location and maintain navigation and executable coverage before doing so. Do not treat the current eight-example test count as an immutable requirement or silently weaken it; any inventory adjustment must reflect the actual documented examples and still execute all of them.

### Verification and stopping boundary

During execution, compare the final README with the pinned review source and map retained technical content to its new home, so consolidation does not silently lose constraints. Review the document at sentence/table, paragraph, section and overall journey levels. Check current active links, including renamed heading anchors, without auditing or changing frozen campaign packages. Run the installed README-example tests for wheel and source-rebuilt variants after executable-example edits; run relevant formatting/lint checks if the test inventory changes. A full runtime suite is not automatically required for prose movement; broaden checks only for actual changed behavior or unresolved coupling.

Current deliverable: publish this proposed plan, present D-001 and the ordered actions, then stop. README and tests remain unchanged. No repair execution, closure, integration, version bump or release is selected by this planning request.

## Execution authorization

The user accepted execution of the proposed plan. D-001 is resolved by the plan's recommended Integration contract title. V-004–V-008 may proceed with per-action verification/publication; stop after V-008 while the campaign remains Open. Earlier planning-only limits are superseded only for these actions; closure, integration and release remain unselected.

## Execution outcome

V-004–V-008 are complete. D-001 uses Integration contract; the two public interfaces and authoritative specification map are retained. Full revision comparison and per-finding rechecks are recorded in REVIEW-REPORT; action/publication evidence is in REVISION-REPORT. All six findings are Verified. Current stop: publish/read back V-008, then remain on the open campaign branch awaiting direction. Earlier proposed-state statements are the retained pre-execution plan, not outstanding tasks.
