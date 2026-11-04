# Important code/docs revision results

Campaign 005_544c112; [review](REVIEW-REPORT.md) and [plan](REVISION-PLAN.md) retain exact baseline evidence, accepted scope and deferred R-004. Working branch revision/005_544c112-code-docs; creation parent/target main. State: all three important revisions verified; final integration/publication completes campaign closure. Original source 544c11280b807fd03c158023c5563dda5d453e34; original opening 8d8bd50d90a03df18ff19f75c93c736ad64c0056.


## V-001 / R-001 — Version-independent release tests

Added one session-scoped project_version fixture reading the authoritative UTF-8 pyproject metadata. Updated native filename/metadata assertions, release checker tag arguments and installed-runtime version assertions in four integration modules. Exact expected versions are still compared against independently built/installed metadata; synthetic historical vectors remain fixed and production/version configuration is unchanged.

Observed RED is the isolated baseline 0.4.1 copy's eight release-integration failures recorded in the review. With only the five revised test/fixture files copied into that same next-version checkout, the release/native/bundle subset plus both installed plain workflows passed all 10 cases in 2.15 seconds. The same 10 cases pass on the current 0.4.0 checkout. Ruff formatting and lint pass for the affected integration files. R-001 is Verified for both versions on Linux; native Windows remains unverified. This containing action commit is published/read back before V-002.


## V-002 / R-002 — Reject symlink staging before writes

prepare_bundles now rejects a symlink output directory at entry, before native validation/checksum generation, directory creation or ZIP writes. Added two actual-filesystem integration regressions for existing and dangling symlink targets, checking target/link preservation and unchanged native input bytes. Both first failed against the old producer: the existing target gained ZIPs, and the dangling link reached mkdir/FileExistsError after native work. After the entry guard, all eight bundle tests pass in 1.10 seconds, including real bundle creation, independent CLI checking and inventory/tamper/checksum faults. Affected lint/format checks pass. R-002 is Verified on Linux; this is a deterministic preflight guard, not an interprocess symlink-race guarantee. This containing action checkpoint is published/read back before V-003.


## V-003 / R-003 — Complete declared test-build prerequisites

Added Hatchling to dev extras and both build/Hatchling to test extras. README now explains why integration tests need the frontend/backend without build isolation. Runtime dependencies and production modules are unchanged. Before repair, a clean temporary environment installed the documented .[dev,test] successfully but failed a real no-isolation build with BackendUnavailable for hatchling.build. After reinstalling only the corrected declared extras into that same environment, the full suite including native builds, independent sdist rebuilds and clean installed consumers passed 713 tests in 28.95 seconds, with 95% production statement/branch coverage. No skips or warnings were reported. This is actual Linux execution, not a configuration-string assertion or Windows certification. R-003 is Verified.

## Complete boundary and integration handoff

All three important findings are Verified; minor R-004 remains Deferred with the review's rationale. Final source/script/test Ruff lint and formatting pass over 74 files; strict mypy passes for 26 source/script files with --no-native-parser. Current maintained document file links and module docstrings pass; all eight README Python examples ran against both installed artifact variants. The complete campaign diff contains only current README/setup configuration, the release producer preflight, affected test fixtures/cases, this campaign's four records and HANDOFF. Prior closed campaign/phase/manual/preparation records and all production modules remain unchanged.

Campaign original baseline/receiving main is 544c11280b807fd03c158023c5563dda5d453e34; original opening is 8d8bd50d90a03df18ff19f75c93c736ad64c0056. V-001 published checkpoint 5e753ea1dcaaf05c35f1483d40ef68282332f0a8; V-002 published checkpoint ee66b9d8cf5bff06d43f5b78ef89d8c820429263. This containing commit completes V-003 and final campaign evidence before explicit two-parent integration from revision/005_544c112-code-docs into refreshed main. Recheck the prospective merged tree and publish/read back the merge; that Git boundary freezes this package. The user's subsequent 0.4.1 release proceeds separately on main without changing these closed records. Exact merge identity, parents and merged checks belong to the integration commit.

Unavailable native Windows/macOS/Python 3.11/3.14/big-endian checks remain explicitly unverified. Prior signal emulation and portable transport checks remain useful evidence of their own mechanisms, not native execution. No confirmed production defect or unresolved important review finding remains in the selected scope; passing local checks do not certify every possible input or platform.
