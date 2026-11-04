# Important code/docs revision results

Campaign 005_544c112; [review](REVIEW-REPORT.md) and [plan](REVISION-PLAN.md) retain exact baseline evidence, accepted scope and deferred R-004. Working branch revision/005_544c112-code-docs; creation parent/target main. State: V-001 verified; V-002 and V-003 pending. Original source 544c11280b807fd03c158023c5563dda5d453e34; original opening 8d8bd50d90a03df18ff19f75c93c736ad64c0056.


## V-001 / R-001 — Version-independent release tests

Added one session-scoped project_version fixture reading the authoritative UTF-8 pyproject metadata. Updated native filename/metadata assertions, release checker tag arguments and installed-runtime version assertions in four integration modules. Exact expected versions are still compared against independently built/installed metadata; synthetic historical vectors remain fixed and production/version configuration is unchanged.

Observed RED is the isolated baseline 0.4.1 copy's eight release-integration failures recorded in the review. With only the five revised test/fixture files copied into that same next-version checkout, the release/native/bundle subset plus both installed plain workflows passed all 10 cases in 2.15 seconds. The same 10 cases pass on the current 0.4.0 checkout. Ruff formatting and lint pass for the affected integration files. R-001 is Verified for both versions on Linux; native Windows remains unverified. This containing action commit is published/read back before V-002.
