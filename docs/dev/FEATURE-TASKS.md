# Lightweight progress logging tasks

[FEATURE-PLAN](FEATURE-PLAN.md) and [FEATURE-SPEC](FEATURE-SPEC.md) govern this bounded Phase 5. IDs continue the project-wide main list after T-052; only this list owns T-053–T-056 during implementation. Existing completed main tasks remain unchanged. All task checks run from the root using the selected interpreter.

- [ ] Phase 5 — Lightweight progress logging
    - [ ] Milestone 5.1 — Progress logging
        - [ ] T-053 — Report bounded scanner progress through standard logging
            - Scope: scanner.py private operation-local observer and logger; tests/unit/test_progress_logging.py; scanner docstrings. Public function signatures and byte/index behavior remain unchanged.
            - Depends on: published accepted feature preparation; existing completed T-052 baseline.
            - Contracts: LOG-01–04 and retained IDX/stream ownership.
            - Acceptance/evidence: Write and observe failing exact-total/timing/disabled-cost/failure tests first, implement the smallest observer/update/finish integration, run them green plus scanner/API regressions and Ruff/mypy. Controlled clocks test 4.999/5.0/large jumps; empty/BOM/short reads, same-chunk dense LF cost, independent scans and invalid/failed reads retain their outcomes. No real-time sleeps or per-line observer calls.
        - [ ] T-054 — Configure scoped CLI progress and logging-level suppression
            - Scope: cli.py --log-level parser and scoped logging context; unit CLI logging tests and affected CLI regression assertions/docstrings.
            - Depends on: T-053.
            - Contracts: LOG-05–06; retained CLI status/output/alias/publication guarantees.
            - Acceptance/evidence: First observe tests fail for default INFO, WARNING suppression, case-insensitive valid/invalid levels, no configuration on help/usage, existing handler/root-state preservation, repeated calls and failure/interruption restoration. Implement scoped package level/owned handler, rerun green and CLI/source/persistence regressions; ensure scan-complete is never a publication-success claim.
        - [ ] T-055 — Verify and document installed progress workflows
            - Scope: actual cross-format/direct-scanner and installed wheel/source-rebuilt command checks; README configuration/suppression guidance; version/install examples 0.5.0. Adapt quiet-stderr assertions to the intentional contract change without weakening status/result checks.
            - Depends on: T-054.
            - Contracts: LOG-01–07, API/CLI installed behavior and milestone 5.1 exits.
            - Acceptance/evidence: Test installed default INFO and WARNING on console/module/imported routes, import/configuration side effects, actual archive totals and unchanged stored pairs. Run complete README examples, package/native checks and relevant failure/lifecycle tests. Perform whole-milestone code review separately from execution, resolve blockers, write reports/5.1.md and HANDOFF, and retain observed checks/native limits with this completion.
    - [ ] Milestone 5.2 — Phase review
        - [ ] T-056 — Review verify and report the complete logging phase
            - Scope: complete Phase 5 coupling, accepted main-document incorporation, completed feature-source archive and current-owner reconciliation, whole-source/package readiness, phase report and HANDOFF.
            - Depends on: T-055 and verified hosted milestone 5.1 closure.
            - Contracts: All LOG conditions, retained main behavior and Phase 5/release exits.
            - Acceptance/evidence: Assess implementation code and logging configuration separately from test results; run full pytest/coverage, Ruff/format, strict mypy and current links. Incorporate resulting scope/API-behavior/CLI/options/physical allocation into main docs with affected conformance rechecks; retain accepted feature sources/QC as historical evidence with corrected in-scope links and unique task ownership. Verify actual source/wheel candidates, naming/checksum contract and intended 0.5.0 notes; audit one initial task checkbox/result commit per T ID and per-commit publication. Persist reports/PHASE-REPORT.md and HANDOFF with this task's initial completion. Integration, exact-source release commit/tag and hosted publication remain pending until their actual verified effects.
