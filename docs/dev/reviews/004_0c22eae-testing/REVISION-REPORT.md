# Testing revision report

## Campaign and result

Campaign `004_0c22eae`, opened on 2026-11-04. [Scope and gates](REVISION-PLAN.md). Working branch `revision/004_0c22eae-testing`; creation parent/integration/return target `main`; full starting code/branch-off `0c22eae396ed04b3d090e287f8c58af79c05f939`.

State: Complete within the three selected focused repairs; final closure is the verified published two-parent integration into main. The opening itself performed no testing. The subsequent user-reported collection failure and pyproject instruction selected V-001; that bounded fix and its checks are now verified below; the subsequent plugin-warning instruction selected verified V-002. The later Windows runner-termination report selected verified V-003 below. Broader testing assessment remains unselected.

## Opening evidence

The worktree was clean and local main matched fetched origin/main at the baseline above. Repository-wide campaign path/ref discovery found reserved sequences 001–003; all their published tips are contained in main, with completed/cancelled closure established by current history and parent HANDOFF. Sequence 004 avoids collision and does not reopen frozen records.

Only this new plan/report and HANDOFF are owned changes. Branch/directory identity, maintained links, Markdown structure and staged diff checks pass. The containing opening commit must be published/read back before further work; its exact identity is recoverable from this package's first commit.

## Current scope and stop

Publish/read back the latest V-003 checkpoint on the active campaign branch, then stop for further instruction. No broader assessment, production repair, main merge/closure or release is selected. Preserve completed task state, closed campaign/phase/manual records and existing releases.

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


## V-003 — Prevent the interruption test killing Windows pytest

Revision entry: published/read-back V-002 `4864798ba10ef79819cb6b0d36c34f8a0b5f3294`. The supplied Windows/CPython 3.14.5 log stops precisely at test_actual_sigint_during_7z_wait_releases_worker. That test invoked os.kill(os.getpid(), signal.SIGINT) inside the pytest process. [Python documents](https://docs.python.org/3.14/library/os.html#os.kill) that Windows uses TerminateProcess for signals other than CTRL_C_EVENT/CTRL_BREAK_EVENT, with the signal value as the exit code. This explains termination before any unit test executes. The earlier ordering/stall diagnosis was incomplete: changing testpaths or collection order would not repair this defect.

The [interruption test](../../../../tests/integration/test_full_format_lifecycle.py) now executes its real blocked-read, KeyboardInterrupt and worker-cleanup assertions in a child interpreter with a 20-second subprocess timeout. It uses signal.raise_signal(signal.SIGINT), retaining a real catchable interrupt. Isolation ensures an abrupt exit becomes an ordinary failed test rather than killing pytest. A second parameter guards against the old transport by substituting Windows hard-exit semantics for os.kill inside the child only. No collection reordering, skips or production changes were introduced.

Observed RED: with the original os.kill call retained inside the new isolated scenario, native Linux passed and the Windows-semantics guard failed with child exit 2 and its TerminateProcess diagnostic; the parent runner survived. Observed GREEN: after replacing that call with signal.raise_signal, both cases passed. This regression exercises the reported failure mechanism rather than asserting configuration text.

The exact pytest console command pytest -vv then completed with 711 passed in 35.60 seconds. Its actual verbose completion lines include 233 integration tests and all 478 unit tests; both interruption parameters passed at 18%, and the first unit test passed at 32%. Ruff lint/format passed over 74 files; strict src/scripts mypy passed over 26 files using --no-native-parser. These are fresh Linux/CPython 3.12.14 results, not native Windows results; the Windows hard-exit behavior was simulated in the child. The latest run did not request coverage; the prior 95% coverage result belongs to V-002.

The containing checkpoint owns this test-harness repair and active campaign continuity/evidence only. Publish/read back on revision/004_0c22eae-testing and stop. Main, production modules, original task state, frozen records, version and releases remain unchanged; the testing campaign remains open.


## Finalization

The human accepted V-003 and requested campaign closure on 2026-11-04. All three bounded repairs are verified and published, most recently V-003 095a2bd623bee106ade80428d7cee925dc205110. No broader testing assessment was performed or implied. The complete delta contains the pytest import/plugin configuration, prerequisite/collection regressions, portable isolated SIGINT test, README installation guidance and this campaign's evidence. It leaves campaigns 001–003, implementation/phase/manual records, product version and releases unchanged. The exact full console run passed 711 tests; final integration repeats the suite on the prospective merged tree. Closure uses the published integration commit and Git parent/readback evidence; a separate comprehensive code/docs campaign and patch release follow under the new user instruction.
