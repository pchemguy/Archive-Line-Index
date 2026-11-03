# TASKS review report

## Current gate

State: **Ready for TASKS acceptance**. The complete list conforms to the accepted PLAN/layout and design/SPEC. Human TASKS acceptance remains pending; no product task is checked, projected to GitHub or selected for implementation. Whole-document-package QC and verified preparation integration remain later gates.

Review date: 2026-11-03. The authoring agent performed hierarchy, contract/owner and dependency review plus document checks. This is not independent code review or evidence that a proposed task has executed.

## Exact reviewed and governing identities

Corrected `TASKS.md` SHA-256: `19ed2de108f58207145cdfe4fb1dbf54bc359d1d65b0eae3cf14a6546b6dc82a`. The initial draft SHA-256 before the bounded correction was `30c9795b0cdcd94c1112c1d850382eb3edc214e36daf534e26a24f7ba50f3e09`.

Accepted scope is recoverable from the published design/SPEC, PLAN/release and layout checkpoints through `63a5669f2cce55b86f168360c9c8e4acffc6f2db`. The current PLAN review metadata records verified layout acceptance/issue closure without changing any governing contract or layout byte. Exact inputs are:

| Governing source | SHA-256 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | `84c2fbe4bb54d38bcc3426dc6460bcd4bb0a045e812502a13a210a5acc5d056c` |
| [ARCHITECTURE.md](ARCHITECTURE.md) | `adf0fab5199e8676cd585ce8ed6652b821f6fcd4590f3a9125a2c5672e85a1db` |
| [DECOMPOSITION.md](DECOMPOSITION.md) | `a9df24ec01f2dc470f020f29ae45e89a6a5b36602aa9cb01ee470be624135af6` |
| [decomposition/public-api.md](decomposition/public-api.md) | `fac8ed1680f4adb2e6e7d251f2aee5e4fa316e2d78a8e6b6bd078da796b4bd44` |
| [decomposition/internal-api.md](decomposition/internal-api.md) | `ef90a5d76bc0456e3f926e439a8983d987c05d65e88df31cb70d3bc7223b16c6` |
| [SPEC.md](SPEC.md) | `70a815a5d4bce2a03e22c31caab6b5853ab441ffc323b9a49c0ed18a5c82dd68` |
| [spec/archive-handling.md](spec/archive-handling.md) | `53eae2d7bb9fe004d4b78987cf379a31062877f7b54c24c38ac9cba981f009df` |
| [spec/cli.md](spec/cli.md) | `5e3f07418eed73e365eacb27c581acc3dd51cab861f6661802977ed920a33a86` |
| [spec/content-stream.md](spec/content-stream.md) | `d080bee124f4c49b86bad070d2edfa3d0ed77efee4ed1c2c00e53c36234bcefd` |
| [spec/line-index.md](spec/line-index.md) | `444c48b11d9645b2a1f4527cb6853c79a1542939f25830112d8c392480ec3735` |
| [spec/persistence.md](spec/persistence.md) | `bb89f91105d4f1593c1ba2462559cf2004cb85a46f28a75d9a2fd8bddfe588bb` |
| [spec/public-api.md](spec/public-api.md) | `611e302b15dc7206ab2367e6bd0054874977fb03f408f8f28a5623a45f3b1303` |
| [PLAN.md](PLAN.md) | `e7e5ed9ebcaa9ed6b30e4644451916203a19cdc99a0f161c3c71babe6db74698` |
| [layout.md](layout.md) | `da78d756af01b8f94ac5b76ea22e8224c55890e6bb6fbff1f1ce59a7db8aa516` |
| [layout/src.md](layout/src.md) | `20ae7203f448683c6d28b9d604963bc601ced5099b494800aae1a17ac208102d` |
| [layout/tests.md](layout/tests.md) | `899b8e26dd9ee98326111519c259c4df620cd33659903fb5612d919d8e34b67b` |
| [layout/docs.md](layout/docs.md) | `43dd9d2618f2784a1c4f539a99ba23bc574e7b28563001f031754291d32b5630` |
| [SPEC-REVIEW-REPORT.md](SPEC-REVIEW-REPORT.md) | `958da59cfe5c94e57714c9e8bf45ecaf8b6bb97956d0ddbe8a25357e96ff2456` |
| [PLAN-REVIEW-REPORT.md](PLAN-REVIEW-REPORT.md) | `c35cab0ddb92533b4182003e88782370adacd01ecd04b8171a048eff9a1c7d60` |

## Initial review

The initial review checked milestone outcome coverage, ownership/path alignment, behavioral size, error/integration/documentation/package work, prerequisite order and all review/release boundaries. It found one localized ownership ambiguity in T-002; no PLAN boundary amendment was needed.

| Finding | Location and consequence | Owning correction and objective recheck | Disposition |
| --- | --- | --- | --- |
| TASK-R001 | T-002 evidence required rejection of malformed archive claims while its scope was only path normalization and bounded detection; this could move full parsing into the detector or require an undelivered adapter. | Keep T-002 responsible for candidate evidence/precedence and absence of plain fallback; require actual validity/rejection in adapter tasks and their consumers. Compare the corrected wording to detector/selection ownership and archive-phase task coverage. | Resolved in Revision 1. |

## Delivery decomposition and review assignments

| Milestone | Delivery tasks | Excluded dedicated review | Review-bearing boundary |
| --- | --- | --- | --- |
| 1.1 | 5 | T-006 | T-006 |
| 1.2 | 3 | None; folded | T-009 (folded) |
| 1.3 | 4 | T-014 | T-014 |
| 2.1 | 5 | T-021 | T-021 |
| 2.2 | 3 | None; folded | T-024 (folded) |
| 2.3 | 3 | None; folded | T-027 (folded) |
| 3.1 | 4 | T-033 | T-033 |
| 3.2 | 5 | T-039 | T-039 |
| 4.1 | 5 | T-046 | T-046 |
| 4.2 | 4 | T-051 | T-051 |

All ten delivery groups contain three to five tasks. The semantic review checked more than counts: one or a few collaborating modules own each increment, with format completion, ownership/failure handling, consumer integration and actual installed artifacts assigned before capability closure. Test/document tasks contribute executable integration or user guidance; dedicated review-only tasks are excluded. No empty group, 1–2 fragmentation case or 10+ overload exists at delivery-task level.

There are 41 delivery tasks, seven dedicated milestone review tasks and four phase review tasks: 52 total. Phase review milestones 1.4, 2.4, 3.3 and 4.3 contain exactly T-015, T-028, T-040 and T-052 respectively. Their dependencies require all delivery milestones complete/closed. The final T-052 additionally owns the full implementation report and cumulative TODO evidence.

The standalone-review threshold is satisfied exactly: every delivery milestone with four/five tasks has a separate dependent review, while the three-task milestones fold whole-capability code review, checks, blocker repair, report and HANDOFF into T-009, T-024 and T-027. Review units remain real selectable tasks; folded obligations do not create replacement administrative units.

## PLAN and acceptance coverage

| Delivery route | Executable coverage and assessment |
| --- | --- |
| Phase 1 plain library | T-001–006 establish actual check/package/error/source/reader/stream foundations. T-007–009 implement canonical offsets and LF/BOM/borrowing/failure behavior. T-010–014 compose and verify installed APIs, source/wheel inventory and public examples. T-015 reviews the usable scoped package and prepares release evidence. API/STR/IDX and applicable SYS obligations have implementation and integrated checks, not only interface stubs. |
| Phase 2 persistence and CLI | T-016–021 implement shared publication and both formats with schema/endianness/corruption/failure checks and public integration. T-022–024 implement importable one-scan paired output, names/preflight, errors and partial publication. T-025–027 deliver console/module/installed behavior and examples. T-028 reviews scoped artifacts and release preparation. PER/CLI and remaining plain-input SYS obligations are covered. |
| Phase 3 ZIP/TAR | T-029–033 provide metadata/reader/integrity and public/CLI ZIP integration. T-034–039 separately provide sequential TAR, trailing validation, required filters and cross-format installed integration. T-040 reviews preservation of preceding capability and release preparation. ARC and archive-dependent STR/IDX/CLI/SYS obligations are extended through actual format consumers. |
| Phase 4 7z/full scope | T-041–046 separate transport/worker mechanics from py7zr metadata/callback integration and real dependency evidence. T-047–051 complete 7z indexing/CLI, full-format lifecycle, documentation/legacy-reference closure and full native artifacts. T-052 verifies the complete accepted system and aggregates final evidence. ARC-06 and remaining concurrency/resource/full-scope obligations are explicitly assigned. |
| Post-integration phase releases | Each phase review prepares release notes, candidates/checksums and reports. TASKS execution boundaries and accepted PLAN require subsequent verified integration, exact-source release finalization, tag/notes/source/wheel publication and hosted-byte verification before a successor starts. These later effects are not falsely marked complete by the review task checkbox and do not add an extra task after the phase review milestone. |

All 49 SPEC conditions retain a delivery/verification route through these groups. Interfaces/models remain with their accepted owners; tasks consume and test them without inventing new public parameters, changing formats or allocating unknown components. Layout paths identify expected scopes and keep production independent of test/CLI/tooling infrastructure where required.

## Revision 1

Corrected T-002 evidence to require bounded candidate classification and claim precedence, with full archive validity/rejection retained by selection/adapters in the appropriate phases. T-003 covers honest unsupported-adapter rejection during the first increment; T-029–038 and T-043–048 cover real archive validation and consumer failures. No task ID, parent, count or accepted strategy changed. The corrected list identity is recorded above.

Recheck found no remaining confirmed conformance issue. IDs are unique and monotonic; all explicit prerequisite IDs exist and refer to earlier tasks; each task has one milestone/phase parent and scope/evidence/contract fields. Milestone reviews depend on their delivery tasks, folded boundaries follow all sibling work and dedicated phase reviews depend on the delivery boundaries. Checklist indentation, local source links, report ownership, exact source identities and unwrapped prose/list items were checked.

## Limits and next gate

No product code, tests, build artifacts, GitHub product-task projection, dependency installation or release has been created. Numeric count/hierarchy checks and document review establish derivation quality, not runtime correctness. TASKS human acceptance precedes whole-package preparation QC; accepted preparation must then be integrated/published and the implementation range selected before eligible-phase activation or execution.
