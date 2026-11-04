# Testing revision campaign

## Campaign and opening scope

- Campaign: `004_0c22eae`; branch: `revision/004_0c22eae-testing`; package: `docs/dev/reviews/004_0c22eae-testing/`.
- Full starting code and branch-off baseline: `0c22eae396ed04b3d090e287f8c58af79c05f939`, matching fetched origin/main.
- Creation parent, eventual integration and return target: actual current `main`.
- Opening request: “open testing revision campaign.” That preparation-only checkpoint was published; the later reported collection failure and pyproject instruction select bounded V-001 below.
- Companion: [REVISION-REPORT.md](REVISION-REPORT.md).
- State: Open; V-001 and V-002 are verified. The broader testing scope has not been assessed or accepted for execution.

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

## Selected action V-001 — Make pytest imports independent of invocation

The human reported four ModuleNotFoundError failures importing scripts from release tests and explicitly identified pyproject as the correction owner. This overrides the opening-only stop for this bounded testing configuration repair. Existing Linux reproduction matches all four errors under the pytest console entry point; python -m pytest collection succeeds because it contributes the current directory to sys.path. The configured pythonpath includes src only.

Add the repository root alongside src in the existing pytest pythonpath, preserving importlib mode, strictness and declared dependencies. Add behavioral subprocess collection regressions without implicit current-directory/PYTHONPATH injection, then run the full suite through the pytest console executable and check module collection. Keep installed consumers isolated; no library/source behavior or governing-contract changes are selected. Record observed RED/GREEN and native limits with the fix, publish/read back on the active testing branch and stop for further instructions. This focused request does not select broader campaign assessment, main integration/closure, version bump or release.

## Selected V-002 — Require the configured pytest plugins

The later plugin-warning report selects V-002 after V-001 publication: reproduce missing plugin diagnostics, require the declared pytest plugins clearly and verify both provisioned and disabled-plugin outcomes. Retain timeout enforcement rather than merely registering an inert marker.

V-002 uses pytest required_plugins for pytest-asyncio and pytest-timeout, which are already declared in the existing dev/test extras. Preserve async/timeout options and effective timeout behavior; do not hide missing enforcement with inert marker registration. Verify each disabled plugin and disabled autoload produce a clear prerequisite error, then run the full provisioned console suite. Document installing extras with the same interpreter; use double quotes in the install command for CMD and shell compatibility. Publish/read back and remain on the active testing branch; no main integration or closure is selected.

## Selected V-003 — Prevent the interruption test terminating Windows pytest

The supplied verbose Windows log stops at test_actual_sigint_during_7z_wait_releases_worker, before unit execution. Source inspection identifies os.kill(os.getpid(), SIGINT); Python documents that on Windows values other than CTRL_C_EVENT/CTRL_BREAK_EVENT use TerminateProcess. Thus the test can kill the entire pytest runner rather than deliver catchable KeyboardInterrupt. The earlier ordering/stall explanation was incomplete.

Keep collection order and all test groups. Isolate the signal/7z cleanup scenario in a bounded child process, retain its real cleanup assertions, and replace self-process kill with signal.raise_signal(SIGINT). Exercise a child-only Windows-kill-semantics guard: the old transport must fail without terminating the parent, while the portable transport completes. Run exact pytest -vv and count actual completed integration/unit lines. Report simulated versus native evidence honestly. This is a focused test-harness repair, not a production or general config change; publish/read back on the active testing branch and stop.
