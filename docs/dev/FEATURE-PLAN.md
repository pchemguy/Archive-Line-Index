# Progress logging delivery plan

Deliver [FEATURE-SPEC](FEATURE-SPEC.md) in one bounded Phase 5 — Lightweight progress logging, package version 0.5.0, retaining the 0.4.1 baseline. This is one coherent cross-cutting capability, not a new platform or archive subsystem.

| Milestone | Outcome and exits |
| --- | --- |
| 5.1 — Progress logging | Scanner observer and exact totals/timing, scoped CLI configuration and suppression, installed-library/command coverage and user guidance. LOG-01–07 and existing relevant scanner/CLI/resource/publication regressions pass. The final delivery task owns whole-milestone code review, tests, report and continuity because only three delivery tasks are needed. |
| 5.2 — Phase review | One dedicated review/testing/report task after delivery and hosted closure. Review coupled behavior, incorporate accepted delta into main documents, retire completed feature sources, run complete tests/coverage/tool/package checks, retain report/HANDOFF and verify task persistence before target integration. |

One delivery milestone is intentional: all changes belong to the same small scanner-to-CLI observation path; splitting logger setup, clocks, handlers or docs into separate milestones would add ceremony without independent user value. Three delivery tasks separate library behavior, CLI behavior and installed/documented distribution validation; each has a localized test-first cycle and meaningful checks. The final review task is excluded from delivery counts. No standalone milestone-review task is justified for three delivery tasks; no padding work is added.

## Verification and release

Use controlled clocks rather than five-second sleeps; test disabled and enabled paths, zero/BOM/short reads, dense LF input, late errors and repeated calls with existing/custom handlers. Verify actual installed console/module/imported routes and source-distribution rebuild outside the checkout. Run full pytest with coverage, Ruff formatting/lint, strict mypy and current doc links/claims. Native Windows/macOS/other Python versions remain unverified unless facilities are available; do not infer native execution from simulations.

After complete verified Phase 5 integration/publication into main, publish v0.5.0 under the existing source/wheel bundle and SHA256SUMS contract. Final notes identify the default CLI stderr change and --log-level WARNING suppression. Rebuild from the exact default-branch release commit, execute the independent complete naming gate, publish/read back tag and release, verify hosted notes/downloaded bytes/latest links. Do not rename native wheel/sdist internals or add versioned outer assets.
