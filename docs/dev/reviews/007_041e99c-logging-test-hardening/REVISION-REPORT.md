# Revision report

## Campaign and state

Campaign 007_041e99c; baseline 041e99c27a6ad8642b08904ad8f325d832db8e6e; working branch revision/007_041e99c-logging-test-hardening, creation parent/return target main. [Accepted plan](REVISION-PLAN.md). State: V-001 verified; V-002 pending. Opening checkpoint 1f7f72221a2e621f04b9dfdf8b4e6ebc4274fad3 was published/read back before execution.

## V-001 — Failed archives never report scan completion

Added explicit absence-of-Scan-complete stderr assertions to corrupt installed ZIP/7z and late-invalid TAR cases, retaining nonzero status, empty success stdout, error diagnostics and no published outputs. Both native-wheel and source-rebuilt installed consumers are exercised across existing CLI routes and filters. Actual archive module run completed all 74 cases successfully; Ruff lint/format passed. A separate test-only invocation injected a false INFO Scan complete record into each actual failed CLI result: all 26 selected cases failed specifically at the new assertion. The injected result preserves the real exit/error/output behavior and changes no production or installed bytes. Thus the assertions detect the intended regression rather than merely matching current success.

Command evidence: python -m pytest tests/integration/test_installed_archives.py -q; controlled invocation of the same selected tests with the _invoke result fault; Ruff on the changed module. Normal output reached 100% with no failures; sensitivity produced exactly 26 expected assertion failures and no collection/setup errors. This action's containing test/evidence checkpoint requires publication/readback before V-002. Native Windows remains unverified.
