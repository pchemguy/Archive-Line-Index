# Project handoff

Checkpoint: Testing revision campaign `003_7c4dcef` is open on `revision/003_7c4dcef-testing`. Scope and initial report are prepared; no assessment, test execution or repair has started. Publish/read back this containing opening commit, then stop.

## Identity, source and authority

Starting code and branch-off: `7c4dcef1c171572e7868d3a03c959ea1c2f87b32`, matching fetched origin/main. Creation parent, eventual integration and return target: actual current `main`. Package: `docs/dev/reviews/003_7c4dcef-testing/`; [plan](reviews/003_7c4dcef-testing/REVISION-PLAN.md), [report](reviews/003_7c4dcef-testing/REVISION-REPORT.md). Branch and directory retain the same full suffix.

The human requested “open testing revision campaign.” Opening only is selected: reserve identity, record testing scope/context and publish. Focus is test coverage/contract mapping, test quality and sensitivity, fixtures, failure/resource/concurrency scenarios, portability and installed-package/example/release-helper testing. No specific repair is accepted yet. Production code and governing contracts are reference inputs; behavior changes are not authorized by this opening.

## Independent work and preserved parent state

Origin has reserved sequence 002 with separate remote branch `revision/002_7c4dcef-code-review-5856224455108738895` at opening `49c033a8ec123cf899c18dae9188d019109f227c`. Preserve it unchanged. This new testing campaign is rooted separately in current main; no nesting/resumption of 002 was selected. No other workflow is suspended or incorporated by this opening.

Campaign 001 completed through published main merge `7c4dcef1c171572e7868d3a03c959ea1c2f87b32`; its records remain frozen. Its 705-test/95% and installed-package evidence is historical baseline evidence, not fresh verification in campaign 003. Preserve original tasks/hosted closures and existing v0.4.0 tag/release at `7ee4afc200c7fded93880397128b0a9e217f3c52`. Do not read or amend closed campaign/phase records without a specific need.

Actual execution host is Linux/bash with existing Python 3.12/py7zr tooling; Windows-only shell instructions apply on Windows hosts. Native target limitations remain unverified rather than inferred from simulations. Markdown prose/list items remain unwrapped; publish/read back every owned commit before advancing.

## Next human boundary

Stop once the opening is published and verified. A later request establishes the testing assessment or concrete revision range; derive evidence-backed actions and verification before editing tests or tooling. No production repair, campaign merge/closure, version bump, release or new runtime provisioning is selected now.
