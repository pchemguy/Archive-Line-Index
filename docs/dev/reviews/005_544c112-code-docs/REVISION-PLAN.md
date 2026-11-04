# Important code/docs revisions

Campaign 005_544c112; original product baseline 544c11280b807fd03c158023c5563dda5d453e34; original opening 8d8bd50d90a03df18ff19f75c93c736ad64c0056. Current entry 88e25eb481d0535be27a17dc87739c7db037ec72. Working branch revision/005_544c112-code-docs; creation parent/integration/return target main. [Review](REVIEW-REPORT.md) contains canonical baseline evidence. User authority covers important fixes, verification, closure and subsequent patch release; no renewed approval is needed for this bounded queue.

| Action | Finding | Changes and objective recheck | Dependencies |
| --- | --- | --- | --- |
| V-001 | R-001 | Shared test metadata reader supplies authoritative version/tag; integration paths/metadata/installed assertions remain exact without hardcoding the current release. Existing isolated 0.4.1 eight-failure reproduction must pass after repairs, including installed workflows. Preserve fixed synthetic/version-notation vectors. | None. |
| V-002 | R-002 | Reject a symlink output directory before producer/native-checksum writes. Add a target-nonmutation regression, observe failure against the old producer and pass after repair; recheck actual bundle build/check. | None; publish V-001 first. |
| V-003 | R-003 | Declare build/Hatchling in test extras and Hatchling in dev extras; clarify README setup. Existing clean extras installation/no-isolation build failure becomes successful build plus real installed integration execution in the same clean environment. | V-001 for next-version test resilience; publish V-002 first. |

R-004 remains deferred as a minor allocation-document recommendation; no governing behavior/layout change is selected. No production functionality, runtime requirements, public API, version bump or frozen-record edits belong to these three actions. The patch version changes only in the later direct-main release operation after campaign closure.

Retain observed RED/GREEN and source/check provenance in REVISION-REPORT.md with each action, commit source/tests/docs and evidence together, then publish/read back before the next action. Recheck composition, full pytest/coverage, Ruff/format and strict mypy, current links and protected-path diff. Finalize continuity and campaign evidence before an explicit two-parent merge into refreshed main; verify and publish main, then freeze campaign records. Complete the separately authorized 0.4.1 release with notes, source/wheel bundles, SHA256SUMS and hosted readback.
