# Project handoff

Checkpoint: Testing campaign 004_0c22eae is complete within its selected V-001–V-003 repairs; this two-parent merge integrates it into main, subject to required target publication/readback. The user requested closure, then a new comprehensive code/docs review, important fixes, closure, a patch version bump and GitHub release.

## Completed testing boundary

[Plan](reviews/004_0c22eae-testing/REVISION-PLAN.md) and [report](reviews/004_0c22eae-testing/REVISION-REPORT.md) retain exact observations and RED/GREEN evidence. Original branch-off 0c22eae396ed04b3d090e287f8c58af79c05f939; opening e1b3b577d476c79d12132213e91a99a619fc19c2; latest repair 095a2bd623bee106ade80428d7cee925dc205110. Working branch revision/004_0c22eae-testing; creation parent/return target main. This containing checkpoint finalizes the report before integration.

Delivered: configured checkout-root imports for console pytest; clear required-plugin diagnostics; same-interpreter installation guidance; portable SIGINT injection isolated in a bounded child so a Windows hard exit cannot kill pytest. Exact pytest -vv passed 711 tests (233 integration and 478 unit), Ruff lint/format passed for 74 files, and strict mypy passed for 26 source/script files using --no-native-parser. Native Windows remains unverified; Windows TerminateProcess behavior was simulated in the child. Prior V-002 coverage was 95%; V-003's exact verbose run did not request coverage.

## Authorized next boundary

Publish/read back this verified main merge (source ee6ac43d48896915aa03fb496dba26b5c96c29a0; receiving parent 0c22eae396ed04b3d090e287f8c58af79c05f939), then freeze campaign 004. The merged full suite passed 711 tests. Open the next allocated comprehensive code/docs campaign on that published baseline, review current production code, tests, supported docs and release tooling, fix important confirmed issues, verify and integrate its complete boundary. Then bump 0.4.0 to 0.4.1 and publish the GitHub release with source and wheel bundles and checksums under the existing release contract. Do not hard-wrap Markdown. Preserve prior closed records and user-owned work. No native Windows result may be inferred from local Linux or simulations.
