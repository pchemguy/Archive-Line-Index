# Revision report

## Campaign and state

Campaign 007_041e99c; baseline 041e99c27a6ad8642b08904ad8f325d832db8e6e; working branch revision/007_041e99c-logging-test-hardening, creation parent/return target main. [Accepted plan](REVISION-PLAN.md). State: both actions and coupled final verification complete; eligible main integration/publication pending. Opening checkpoint 1f7f72221a2e621f04b9dfdf8b4e6ebc4274fad3 was published/read back before execution.

## V-001 — Failed archives never report scan completion

Added explicit absence-of-Scan-complete stderr assertions to corrupt installed ZIP/7z and late-invalid TAR cases, retaining nonzero status, empty success stdout, error diagnostics and no published outputs. Both native-wheel and source-rebuilt installed consumers are exercised across existing CLI routes and filters. Actual archive module run completed all 74 cases successfully; Ruff lint/format passed. A separate test-only invocation injected a false INFO Scan complete record into each actual failed CLI result: all 26 selected cases failed specifically at the new assertion. The injected result preserves the real exit/error/output behavior and changes no production or installed bytes. Thus the assertions detect the intended regression rather than merely matching current success.

Command evidence: python -m pytest tests/integration/test_installed_archives.py -q; controlled invocation of the same selected tests with the _invoke result fault; Ruff on the changed module. Normal output reached 100% with no failures; sensitivity produced exactly 26 expected assertion failures and no collection/setup errors. This action's containing test/evidence checkpoint requires publication/readback before V-002. Native Windows remains unverified.

## V-002 — Observe initial package-import logging state

Moved the root logger level/handler snapshot before the first archive_line_index import in the fresh isolated installed consumer and asserted preservation immediately after that import. The same original snapshot still verifies CLI import and repeated imported CLI execution; existing index assertions remain intact. All 13 progress integration cases passed in 4.46 seconds, including six installed package-variant/route combinations. Ruff lint/format passed.

A test-only import wrapper deliberately changed root level to DEBUG immediately after the first real archive_line_index import in each fresh installed process. All six installed cases failed at the newly positioned immediate post-import assertion (subprocess line 16); real package imports, CLI runs and output checks otherwise execute normally. This demonstrates coverage of the previously missed initial import rather than a later CLI-only comparison. No production code or installed package file was modified. V-001 checkpoint 4ad8bb3fdbcd294ce1dd163702ad890a4ff6a78c was published/read back before this action. This action's containing checkpoint requires publication/readback before coupled finalization.

## Final verification and disposition

Both accepted findings are Verified in this campaign; neither remains deferred. V-002 checkpoint fcaf692e834397436defafeb0adf7e3c46895f95 was published/read back before final verification. Full regression: 755 tests passed in 38.84 seconds with 95% production statement/branch coverage. Ruff lint passed, all 77 files were already formatted, and strict mypy --no-native-parser passed 26 source/script files. Actual execution was Linux/CPython 3.12.14; native Windows remains unverified.

Final source inspection confirms exactly three negative archive-log assertions and a pre-import root snapshot/immediate comparison; no error/status/output/index checks were removed. Controlled sensitivity failures are expected fault-injection evidence, not unresolved normal-suite failures. Production code, versions, releases, canonical requirements/tasks and prior closed campaign/feature records are unchanged. Existing tests were strengthened; the total remains 755 rather than increasing.

The original opening is 1f7f72221a2e621f04b9dfdf8b4e6ebc4274fad3; branch-off/receiving main baseline is 041e99c27a6ad8642b08904ad8f325d832db8e6e. Final campaign records/HANDOFF are complete in this containing checkpoint and require publication/readback, followed by explicit two-parent main integration. Its merge message and parent HANDOFF will own subsequent merge checks/publication facts; do not retrospectively edit this closed report. No version bump/release is part of this test-only maintenance campaign.
