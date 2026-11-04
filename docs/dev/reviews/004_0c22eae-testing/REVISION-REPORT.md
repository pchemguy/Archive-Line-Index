# Testing revision report

## Campaign and result

Campaign `004_0c22eae`, opened on 2026-11-04. [Scope and gates](REVISION-PLAN.md). Working branch `revision/004_0c22eae-testing`; creation parent/integration/return target `main`; full starting code/branch-off `0c22eae396ed04b3d090e287f8c58af79c05f939`.

State: Open. The opening itself performed no testing. The subsequent user-reported collection failure and pyproject instruction selected V-001; that bounded fix and its checks are now verified below; the subsequent plugin-warning instruction selected verified V-002. Broader testing assessment remains unselected.

## Opening evidence

The worktree was clean and local main matched fetched origin/main at the baseline above. Repository-wide campaign path/ref discovery found reserved sequences 001–003; all their published tips are contained in main, with completed/cancelled closure established by current history and parent HANDOFF. Sequence 004 avoids collision and does not reopen frozen records.

Only this new plan/report and HANDOFF are owned changes. Branch/directory identity, maintained links, Markdown structure and staged diff checks pass. The containing opening commit must be published/read back before further work; its exact identity is recoverable from this package's first commit.

## Current scope and stop

Publish/read back the V-001 checkpoint on the active campaign branch, then stop for further instruction. No broader assessment, production repair, main merge/closure or release is selected. Preserve completed task state, closed campaign/phase/manual records and existing releases.

## V-001 — Fix pytest collection imports

Revision entry: opening commit `e1b3b577d476c79d12132213e91a99a619fc19c2`. The human supplied four release-test collection errors (ModuleNotFoundError: scripts), then directed the fix to pyproject. Both reports match an actual local reproduction: the standalone pytest console executable exits 2 with those four import errors, while python -m pytest collects successfully. The existing pythonpath included src only; module invocation implicitly contributes cwd, masking the checkout-root dependency. This is not demonstrated to be Windows-specific.

Added the repository root alongside src in [pyproject.toml](../../../../pyproject.toml), retaining importlib mode, strict configuration/markers and dependencies. [Invocation regressions](../../../../tests/integration/test_pytest_entrypoints.py) collect the affected release tests in child interpreters without implicit cwd insertion or inherited PYTHONPATH, both from the checkout and an external directory. Both new cases first failed with the same four import errors; after the configuration change they pass. The regressions exercise collection behavior, not configuration-string matching.

| Check | Actual result |
| --- | --- |
| Before fix: pytest --collect-only from checkout | Exit 2; four scripts import errors matching the user report. |
| Before fix: python -m pytest collection | Passed; explains the earlier 705-test module-invocation result. |
| New safe-path and outside-checkout regressions before fix | 2 failed with collection exit 2 and the same four errors. |
| After fix: full pytest console executable with strict config/markers and coverage | 707 passed in 38.73 seconds; 95% production coverage. Includes both new regressions, actual package builds/source-wheel rebuilds/installed consumers and README examples. |
| After fix: python -m pytest --collect-only | 707 collected successfully. |
| Ruff lint/format | Passed; 74 files formatted. |
| Strict src/scripts mypy | Passed, 26 files, --no-native-parser for the known container parser issue. |

Actual execution remains Linux/CPython 3.12.14 with pytest 9.2.0 and py7zr 1.1.4. Native Windows execution is not claimed. Configured test imports do not modify installed consumers: those still execute isolated interpreters outside the checkout without source-path injection. No production modules, version, runtime dependencies, original task state or frozen records changed. The containing commit publishes this bounded fix and evidence; remain on the active testing branch afterward.

## V-002 — Required plugin diagnostics

The human subsequently supplied unknown asyncio/timeout option and timeout-marker warnings. After V-001 publication, assess the missing/not-loaded declared plugins and add a clear prerequisite failure rather than masking missing timeout enforcement. The existing interpreter must contain and load its declared test dependencies; this queued instruction is not a request to remove the configured timeout behavior. No V-002 change is included in the V-001 checkpoint.

### V-002 observed execution

Revision entry: published/read-back V-001 `b112e9ad6c6f8650c6aec8707d032753b9ac674a`. The supplied unknown asyncio/timeout options and timeout marks indicate missing or not-loaded test plugins, despite their existing declarations in dev/test extras. No new dependency declaration was needed. The configuration now requires pytest-asyncio and pytest-timeout explicitly before collection. README explains same-interpreter installation and uses double quotes for the extras command, compatible with CMD as well as the shell.

Three new child-process regressions first failed because disabling asyncio, timeout or all third-party autoload produced unknown option/marker errors instead of the expected prerequisite diagnostic. After required_plugins was added, each exits with pytest usage code 4 and names the missing required plugin(s), without PytestConfigWarning or PytestUnknownMarkWarning. Existing positive safe-path/external-cwd collection cases also pass; all five invocation/prerequisite checks are green. Missing plugin behavior is not “fixed” by suppressing warnings or pretending the timeout marker still enforces a limit.

The full provisioned pytest console run passes 710 tests in 30.92 seconds at 95% production coverage. Ruff lint/format over 74 files and strict src/scripts mypy over 26 files pass. Actual execution is Linux/CPython 3.12.14 with pytest 9.2.0 and py7zr 1.1.4; native Windows execution remains unverified. This repository change cannot install or enable plugins on the user's workstation: use python -m pip install ".[dev,test]" with the same interpreter used by pytest, and ensure the required plugins are loaded.

The containing V-002 commit owns pyproject, README, behavioral regressions and current campaign evidence. Production modules, runtime dependencies/version, task state and frozen records are unchanged. Publish/read back this checkpoint on revision/004_0c22eae-testing and stop; the campaign remains open.
