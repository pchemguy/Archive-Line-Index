# Revision plan

## Campaign and authorization

Campaign 007_041e99c; branch revision/007_041e99c-logging-test-hardening; creation parent and integration target main at full baseline 041e99c27a6ad8642b08904ad8f325d832db8e6e. The user requested opening a revision campaign to implement both deferred minor regression-coverage suggestions. This directly accepted focused maintenance needs no invented review stage, new feature preparation or product requirement changes.

The accepted suggestions are 006_c33ec54/M-001 (corrupt installed ZIP/TAR/7z cases must explicitly reject Scan complete records) and 006_c33ec54/M-002 (snapshot root logging before initial package import in the installed progress test). Current behavior was previously probed correct; these are coverage gaps, not confirmed production defects. Their original closed feature sources and reports remain unchanged.

## Ordered actions

| Action | Finding | Change | Verification |
| --- | --- | --- | --- |
| V-001 | 006_c33ec54/M-001 | Assert no Scan complete record in existing corrupt ZIP/7z and late-invalid TAR installed CLI cases, retaining error/output/publication assertions. | Actual wheel/source-rebuilt archive checks; controlled false-completion output must fail the new assertion. |
| V-002 | 006_c33ec54/M-002 | Capture root state before first archive_line_index import and assert preservation immediately after package import, retaining CLI import/invocation checks. | All installed routes and package variants; injected import-time root mutation must fail. |

## Execution and stop

[REVISION-REPORT.md](REVISION-REPORT.md) owns action evidence. Commit each action with its verification, publish/read back before continuing, then run full relevant regression and code checks, finalize reports/HANDOFF and explicitly merge/verify/publish main. No production behavior, package version or existing release changes are selected; this maintenance campaign allocates no executable T tasks or phase. Preserve prior closed packages. Stop after verified integration and clean return to main. Native Windows execution remains unverified.
