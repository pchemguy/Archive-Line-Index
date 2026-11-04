# Project handoff

Checkpoint: Active testing campaign `004_0c22eae` has verified V-001 collection imports and V-002 plugin prerequisites. Publish/read back this containing V-002 checkpoint on `revision/004_0c22eae-testing`, then stop for further instruction. The broader campaign remains open; no merge/closure or release is selected.

## Source and selected instructions

Original source/branch-off `0c22eae396ed04b3d090e287f8c58af79c05f939`; original opening `e1b3b577d476c79d12132213e91a99a619fc19c2`; published V-001 `b112e9ad6c6f8650c6aec8707d032753b9ac674a`; creation parent/target `main`. [Plan](reviews/004_0c22eae-testing/REVISION-PLAN.md) and [report](reviews/004_0c22eae-testing/REVISION-REPORT.md) retain root causes, observed RED/GREEN and scope. The human reported four scripts import errors, said pyproject needs something, then supplied missing-plugin warnings; these selected the two bounded testing-configuration repairs beyond opening-only scope.

V-001: pythonpath now includes src and checkout root. Standalone pytest reproduced the exact four import errors while python -m pytest collection passed; the implicit cwd path masked the defect in earlier verification. Two child-process regressions without implicit cwd/PYTHONPATH insertion fail before and pass after, from both checkout and external cwd. Full console run then passed 707 tests at 95% coverage.

V-002: required_plugins now requires already-declared pytest-asyncio and pytest-timeout before collection. Three disabled-plugin/autoload regressions first failed, then produced clear usage-code-4 prerequisite diagnostics without unknown-option/marker warnings. Both positive invocation cases remain green. README documents same-interpreter extras installation with double quotes for CMD/shell compatibility; no warning suppression or inert timeout-marker registration was introduced.

## Verified results and limits

Latest full pytest console run: 710 passed, 95% production coverage, including actual builds/source-wheel rebuilds, isolated installed consumers and README examples. All five invocation/prerequisite regressions pass; Ruff lint/format over 74 files and strict src/scripts mypy over 26 files pass (--no-native-parser). Actual runtime is Linux/CPython 3.12.14, pytest 9.2.0 and py7zr 1.1.4; no native Windows execution is claimed.

The user's interpreter still must install/load the declared extras; pyproject cannot install them automatically. Use python -m pip install ".[dev,test]" with the interpreter that runs pytest. Required-plugin checks detect disabled/missing plugins instead of silently dropping timeout behavior. Production source, runtime dependency/version, existing task/hosted closures, closed campaign/phase/manual records and v0.4.0 remain unchanged.

## Stop

Publish/read back the focused V-002 checkpoint and remain on the active testing branch. No broader testing assessment, additional repair, main integration/closure, version bump or release is selected. Await the next instruction. Markdown prose/list items remain unwrapped.
