# Testing revision campaign

## Identity and opening scope

- Campaign: `003_7c4dcef`; branch: `revision/003_7c4dcef-testing`; package: `docs/dev/reviews/003_7c4dcef-testing/`.
- Starting code and full branch-off baseline: `7c4dcef1c171572e7868d3a03c959ea1c2f87b32`, matching fetched origin/main.
- Creation parent, eventual integration and return target: current published `main`.
- Request: “open testing revision campaign.” This checkpoint reserves the campaign, records its testing scope and HANDOFF, commits/publishes/read backs, then stops. No testing assessment, repair, environment provisioning, merge or release is selected by opening alone.
- [Revision report](REVISION-REPORT.md) records actual progress. State: Open; preparation only, no implementation action accepted or executed.

## Testing focus

| Area | Intended assessment boundary |
| --- | --- |
| Coverage and contract mapping | Identify meaningful omissions in public API, streaming, LF/BOM/EOF offsets, archive integrity, persistence and CLI coverage against accepted contracts. Distinguish missing coverage from demonstrated production defects. |
| Test quality | Check independent expected values, fixture fidelity, sensitivity to plausible faults, negative cases, assertions, excessive mocking, duplication and deterministic failure diagnostics. |
| Resource and concurrency testing | Assess startup/cleanup/cancellation/join, retained failures, publication commit points, races and bounded-storage checks without confusing dependency allocations or simulations with native behavior. |
| Portability and environment | Record exact Python/pytest/dependency/plugin versions, platform restrictions, long parameter IDs, locale/endian handling and actual versus simulated Windows behavior. |
| Test execution and package consumers | Assess unit/integration selection, markers/timeouts, installed wheel/source-rebuild workflows, example tests and release-helper tests using existing declared tooling. |

Production code and current governing contracts are reference inputs for testing, not authorized behavior-change targets. Changes to test strategy, fixtures, test cases, test tooling/configuration or testing guidance require a concrete evidence-backed action plan when further work is requested. Runtime defects discovered during testing must be reported separately rather than silently repaired or used to expand this campaign.

## Preparation and execution gates

A subsequent testing instruction establishes the exact assessment/repair range. Inspect current tests and relevant contracts, run proportionate checks in the existing runtime, and distinguish inspected coverage, fresh execution and historical results. Derive bounded proposed test revisions from actual evidence; do not allocate invented findings or claim that the inherited passing suite certifies this campaign.

For authorized changes, record stable action IDs, expected failures/outcomes, affected test owners and objective rechecks before implementation. Add tests for meaningful behavior; avoid tests that merely mirror implementation, arbitrary coverage-percentage targets or fabricated RED evidence. Publish/read back each owned checkpoint before advancing. New production behavior or governing-contract changes return for an explicit decision through their owning workflow.

After separately authorized execution and feasible verification, complete campaign evidence before an explicit two-parent merge into refreshed main and verified publication. Keep records in this package and preserve closed campaigns. Opening itself stops before those operations.

## Parallel work and evidence limits

Campaign sequence 002 is already reserved by the separate remote code-review branch `revision/002_7c4dcef-code-review-5856224455108738895`, opening commit `49c033a8ec123cf899c18dae9188d019109f227c`. This testing campaign is separately rooted at the current main context; no parent campaign was selected in the request. Preserve 002 unchanged; its existence does not authorize resuming, nesting into, suspending or merging it. Do not consume its later conclusions without pinning their source and assessing relevance.

Campaign 001 is closed and its records remain frozen. Prior implementation evidence reports 705 passing tests and 95% coverage at this baseline; no test has been rerun here. Actual available host is Linux/bash with the existing CPython 3.12/py7zr tooling. Unavailable Windows/macOS/Python 3.11/Python 3.14/big-endian execution remains unverified; simulations do not certify those targets. Preserve original task/tracking closures and the v0.4.0 tag/release. No version bump or release is selected.
