# Testing revision campaign

## Campaign and opening scope

- Campaign: `004_0c22eae`; branch: `revision/004_0c22eae-testing`; package: `docs/dev/reviews/004_0c22eae-testing/`.
- Full starting code and branch-off baseline: `0c22eae396ed04b3d090e287f8c58af79c05f939`, matching fetched origin/main.
- Creation parent, eventual integration and return target: actual current `main`.
- Request: “open testing revision campaign.” Authorized now: reserve a new campaign, record testing scope and entry HANDOFF, commit/publish/read back and stop. No testing assessment, test execution or implementation is selected by opening alone.
- Companion: [REVISION-REPORT.md](REVISION-REPORT.md).
- State: Open, preparation only. No finding, repair action or test revision has been accepted or executed.

## Testing scope

| Area | Intended assessment |
| --- | --- |
| Contract coverage | Assess meaningful positive/negative coverage for public APIs, source detection, streaming, LF/BOM/EOF offsets, all archive families, persistence and CLI. Distinguish coverage omissions from actual runtime defects. |
| Test quality | Assess independent expectations, fixture fidelity, useful assertions, fault sensitivity, determinism, excessive mocking/duplication and failure diagnostics. |
| Failure and resource scenarios | Assess opening/startup/terminal failures, owned versus borrowed resources, cancellation/join, retained errors, filesystem races, publication commit points and bounded-storage evidence. |
| Portability and tooling | Record actual Python/pytest/dependency/plugin versions, parameter-ID bounds, locale/endian behavior, native platform limits and faithful versus simulated dependencies. |
| Installed consumers | Assess wheel/source-rebuild workflows, outside-checkout imports, all CLI forms, README examples and release-helper checks using declared project tooling. |

Production code and accepted design/contracts are reference inputs, not selected behavior-change targets. Later testing revisions may concern test strategy, cases, fixtures, tooling/configuration and testing guidance once actual evidence and bounded actions are established. Report runtime defects separately; do not silently expand into product repairs or change governing contracts.

## Further-work gates

A subsequent instruction selects assessment or implementation scope. Before changes, inspect current tests and relevant contracts, pin the candidate, record exact environment capabilities, derive concrete actions and objective rechecks, and distinguish source inspection, fresh execution, simulation and historical evidence. Do not infer defects from coverage percentages or create tests that merely mirror implementation. Use test-first evidence where meaningful and label characterization honestly.

For authorized actions, preserve stable IDs, source/test ownership and observed results in the report; publish/read back each owned checkpoint before advancing. A later complete verified campaign integrates explicitly into refreshed recorded parent main. Opening itself stops before those actions and before any merge, closure or release.

## Preserved history and limits

Sequences 001–003 are reserved and their published tips are contained in main: 001 completed; 002 and 003 were cancelled. Their records remain frozen; this is a new campaign, not reopening or resuming cancelled testing work. No active parent campaign or nesting context is selected.

The product baseline retains prior 705-test/95% evidence, not fresh execution in campaign 004. Actual available host is Linux/bash with existing CPython 3.12/py7zr tooling. Unavailable Windows/macOS/Python 3.11/Python 3.14/big-endian execution remains unverified; simulations do not certify those platforms. Preserve original task/hosted closures and existing v0.4.0. No new runtime provisioning, version bump or release is selected.
