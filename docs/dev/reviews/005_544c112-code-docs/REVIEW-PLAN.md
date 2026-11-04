# Comprehensive code and documentation review plan

## Campaign and authority

Campaign 005_544c112; full starting/reviewed source 544c11280b807fd03c158023c5563dda5d453e34, following verified published closure of testing campaign 004. Working branch revision/005_544c112-code-docs; creation parent/integration/return target main. The human requested a comprehensive code/docs review, important fixes, closure, patch bump and GitHub release; review and bounded correction checkpoints are preapproved for that scope. This campaign closes before the separate direct-main 0.4.1 release operation.

## Units and criteria

| Unit | Scope and order | Criteria and scenarios | Evidence |
| --- | --- | --- | --- |
| U-001 | All production modules; accepted PROJECT, ARCHITECTURE, DECOMPOSITION, SPEC and focused contracts | Stream lifecycle, archive selection, integrity/errors, cancellation/backpressure; scanner offsets/BOM/EOF; raw/SQLite validation and atomic publication; API/CLI success/failure/limits | Read every production module and relevant contracts; run full baseline tests and targeted independent boundary probes. |
| U-002 | All test modules/fixtures and release scripts/configuration | Meaningful positive/negative coverage, subprocess isolation/platform behavior, distribution metadata/membership, naming/checksum/bundle verification, safe archive handling and release provenance | Inspect test inventory and fixture/harness seams; run lint/types; exercise build and package checks with actual outputs and adversarial inputs where warranted. |
| U-003 | README, current design/spec/plan/layout docs, instruction/tooling guidance, release/install docs and cross-component composition | Supported claims/examples/defaults match code and contracts; useful navigation/docstrings; no current contradictions or broken local links; no credential/internal packaging leak | Inspect current documents and all module docstrings, check active links, run examples through installed-consumer tests and consolidate findings. |

Third-party dependency internals and bundled SDD Manager instructions are not product repair targets. Closed review/feature/phase/manual/preparation evidence is frozen and excluded from current-validity checks; inspect its paths only to protect it. No native Windows/macOS/Python 3.11/3.14 host is available; record simulations separately from actual Linux/CPython 3.12 execution. No new product scope or requirement changes are implied. Important means confirmed defects with material correctness, reliability, test, documentation or distribution impact; optional style churn is deferred.

## Persistence and execution

After each unit, retain exact source, inspected coverage, no-finding evidence and located stable findings R-001 onward in REVIEW-REPORT.md; commit, publish and verify remote readback before the next unit. Consolidate an ordered REVISION-PLAN.md with action IDs and objective rechecks, implement authorized important fixes using observed RED/GREEN for behavioral defects, and retain actual results in REVISION-REPORT.md. Preserve baseline observations separately from later dispositions.

Run affected and full regression checks, verify the complete diff leaves closed records untouched, finalize continuity and campaign evidence, then explicitly merge the verified complete boundary into refreshed main, verify and publish/read back. After closure, bump patch version and prepare notes from complete Git changes since v0.4.0, build and verify the exact release source, publish its default-branch commit/tag and GitHub release with stable source/wheel ZIP bundles plus SHA256SUMS. Check hosted bytes, body, tag and latest links before claiming completion. No Markdown prose hard wrapping.
