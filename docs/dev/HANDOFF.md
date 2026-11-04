# Project handoff

Checkpoint: Active testing campaign `004_0c22eae` has verified bounded V-001, repairing the user-reported pytest collection failure. Publish/read back this containing fix/evidence checkpoint on `revision/004_0c22eae-testing`, then handle the newly reported plugin-warning diagnostics as queued V-002. The broader campaign remains open and unassessed; no merge/closure is selected.

## Source and authority

Original source/branch-off `0c22eae396ed04b3d090e287f8c58af79c05f939`; original opening `e1b3b577d476c79d12132213e91a99a619fc19c2`; creation parent/target `main`. [Revision plan](reviews/004_0c22eae-testing/REVISION-PLAN.md) and [report](reviews/004_0c22eae-testing/REVISION-REPORT.md) record the focused action, root cause and actual checks. The human supplied four scripts import errors and said pyproject needs something, authorizing this testing-configuration fix beyond opening-only scope.

The standalone pytest console executable reproduced the exact four ModuleNotFoundError failures; python -m pytest collection passed because implicit cwd insertion masked the missing checkout root. Pytest pythonpath now includes src and the repository root. Two child-process collection regressions without implicit cwd/PYTHONPATH insertion failed before the fix and pass after it, from both checkout and external cwd. Product behavior is unchanged.

## Verified outcome and limits

The full console pytest run passes 707 tests with 95% production coverage, including package builds/source-wheel rebuilds, outside-checkout installed consumers and README examples. Module invocation collects all 707 tests. Ruff lint/format over 74 files and strict src/scripts mypy over 26 files pass (--no-native-parser). Actual runtime is Linux/CPython 3.12.14, pytest 9.2.0 and py7zr 1.1.4; this is not a native Windows execution claim. Earlier 705-test results used python -m pytest and did not cover the console collection path.

Production modules, versions/dependencies, existing tasks/hosted closures, closed campaigns 001–003, phase/manual records and v0.4.0 remain unchanged. Installed consumer isolation is preserved. Markdown prose/list items remain unwrapped.

## Stop

Publish/read back the focused fix and remain on the active testing campaign branch. No broader assessment, additional repair, main integration/closure, version bump or release is selected. Await the next human instruction.

## Queued user steering

The human also reported unknown asyncio/timeout config options and timeout marks. After publishing V-001, execute bounded V-002: require the already-declared plugins with a clear failure and verify missing/not-loaded versus correctly provisioned outcomes. Do not weaken timeout enforcement to hide the warning.
