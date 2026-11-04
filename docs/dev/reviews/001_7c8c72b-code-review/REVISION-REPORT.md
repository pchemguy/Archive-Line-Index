# Revision report

## Campaign and result

Campaign: `001_7c8c72b`; [plan](REVISION-PLAN.md), [review and corrections](REVIEW-REPORT.md). Original baseline `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`; original opening `7eedb5efdb5e8ce1a6b8ef333a25c9f36c3fb70c`; revision entry `227774e18440c61041efcd91adb46be7fff95026`. Working branch `revision/001_7c8c72b-code-review`; creation parent/return target `main`. State: planned execution; no source repair yet.

The human authorized plan preparation and execution after the assessment. Existing Linux/CPython 3.12.14 with py7zr 1.1.4 is the actual execution runtime; previous Windows results remain attributed review evidence. No governing-document amendment or new TASKS is required. Preserve original observations and frozen prior phase/manual records.

## Action index

| Action | State | Evidence |
| --- | --- | --- |
| V-001 | Verified planning | Review source/config comparisons, seven-action plan, selected dispositions, maintained local links and staged diff checks; containing planning commit is the checkpoint. |
| V-002 | Verified | R-007; see revision plan. |
| V-003 | Verified | R-001, R-002; see revision plan. |
| V-004 | Planned | R-004; see revision plan. |
| V-005 | Planned | R-005; see revision plan. |
| V-006 | Planned | R-008 encoding only; see revision plan. |
| V-007 | Planned | All accepted actions; R-006 evidence; see revision plan. |

## Action evidence

### V-001 — Planning and evidence reconciliation

Recorded selected corrections without rewriting original review observations, including false pytest configuration claims, missing CLI helper, incorrect sdist inventory and dependency constraint. Narrowed ZIP counter acceptance and plain-buffer interpretation; deferred R-003 and retained native limitations. Maintained campaign links/identity, Markdown structure and diff composition pass. No source/test/script/config changes are included. Publish/read back the containing commit before V-002.

## Remaining work and limits

V-002–V-007 remain. Actual target-native Windows and Python 3.14 execution are unavailable; simulations and existing Linux checks do not certify them. R-003 remains deferred by the selected scope. No version bump or release is selected. Final integration/closure waits for accepted repairs and feasible verification.

### V-002 — Fix Windows-compatible SQLite synchronization

Revision source: `58a05c80d0a08b190eeaf08df27f3a61326c3ede` plus this action’s owned diff. Two new create/overwrite regressions first failed with EBADF under a portable Windows writable-fsync precondition. A non-truncating writable temporary descriptor and widened internal mode annotation now pass both cases, preserving exact reloaded offsets, borrowed arrays and cleanup. All 159 focused persistence/filesystem/CLI/TAR checks, strict src/scripts mypy and Ruff lint/format pass after formatting repair. Real SQLite/fsync/publication runs on Linux; fresh native Windows execution remains unverified.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-003 — Bound source inspection and plain-file buffering

Revision source: `e3110f88b6f411886279b4c3628ea17b7511b909` plus this action’s owned diff. Three raw-I/O regressions first failed because read(512) requested a 128 KiB underlying buffer. The larger-default plain-stream regression separately failed at 150541 traced bytes. Explicit unbuffered detection now fills at most 512 bytes across legal short reads and unbuffered plain delivery avoids runtime-dependent read-ahead. Raw traces for chunks 1/17/512, both 8 KiB/128 KiB simulated defaults, long-line scanning and all 104 selected detector/plain/public/ZIP/TAR/7z checks pass. Strict src/scripts mypy and Ruff lint/format pass. Python 3.14 behavior is simulated on Python 3.12, not claimed native-verified; no universal 128 KiB product memory cap is introduced.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.
