# Revision report

## Campaign and result

Campaign: `001_7c8c72b`; [plan](REVISION-PLAN.md), [review and corrections](REVIEW-REPORT.md). Original baseline `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`; original opening `7eedb5efdb5e8ce1a6b8ef333a25c9f36c3fb70c`; revision entry `227774e18440c61041efcd91adb46be7fff95026`. Working branch `revision/001_7c8c72b-code-review`; creation parent/return target `main`. State: V-001–V-006 individually published/read back and V-007 source plus prospective main-merge verification complete. Campaign closure requires publication/readback of the containing explicit main merge.

The human authorized plan preparation and execution after the assessment. Existing Linux/CPython 3.12.14 with py7zr 1.1.4 is the actual execution runtime; previous Windows results remain attributed review evidence. No governing-document amendment or new TASKS is required. Preserve original observations and frozen prior phase/manual records.

## Action index

| Action | State | Evidence |
| --- | --- | --- |
| V-001 | Verified planning | Review source/config comparisons, seven-action plan, selected dispositions, maintained local links and staged diff checks; containing planning commit is the checkpoint. |
| V-002 | Verified | R-007; see revision plan. |
| V-003 | Verified | R-001, R-002; see revision plan. |
| V-004 | Verified | R-004; see revision plan. |
| V-005 | Verified | R-005; see revision plan. |
| V-006 | Verified | R-008 encoding only; see revision plan. |
| V-007 | Verified source and merged state; main publication required | All accepted actions; R-006 evidence; see revision plan. |

## Action evidence

### V-001 — Planning and evidence reconciliation

Recorded selected corrections without rewriting original review observations, including false pytest configuration claims, missing CLI helper, incorrect sdist inventory and dependency constraint. Narrowed ZIP counter acceptance and plain-buffer interpretation; deferred R-003 and retained native limitations. Maintained campaign links/identity, Markdown structure and diff composition pass. No source/test/script/config changes are included. Publish/read back the containing commit before V-002.

## Remaining work and limits

All selected source/test/script repairs and merged-state verification are complete. V-007 main merge commit/publication remains. Actual target-native Windows and Python 3.14 execution are unavailable; portable simulations and Linux checks do not certify them. R-003 remains deferred. No version bump or release is selected.

### V-002 — Fix Windows-compatible SQLite synchronization

Revision source: `58a05c80d0a08b190eeaf08df27f3a61326c3ede` plus this action’s owned diff. Two new create/overwrite regressions first failed with EBADF under a portable Windows writable-fsync precondition. A non-truncating writable temporary descriptor and widened internal mode annotation now pass both cases, preserving exact reloaded offsets, borrowed arrays and cleanup. All 159 focused persistence/filesystem/CLI/TAR checks, strict src/scripts mypy and Ruff lint/format pass after formatting repair. Real SQLite/fsync/publication runs on Linux; fresh native Windows execution remains unverified.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-003 — Bound source inspection and plain-file buffering

Revision source: `e3110f88b6f411886279b4c3628ea17b7511b909` plus this action’s owned diff. Three raw-I/O regressions first failed because read(512) requested a 128 KiB underlying buffer. The larger-default plain-stream regression separately failed at 150541 traced bytes. Explicit unbuffered detection now fills at most 512 bytes across legal short reads and unbuffered plain delivery avoids runtime-dependent read-ahead. Raw traces for chunks 1/17/512, both 8 KiB/128 KiB simulated defaults, long-line scanning and all 104 selected detector/plain/public/ZIP/TAR/7z checks pass. Strict src/scripts mypy and Ruff lint/format pass. Python 3.14 behavior is simulated on Python 3.12, not claimed native-verified; no universal 128 KiB product memory cap is introduced.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-004 — Validate observable ZIP payload size before completion

Revision source: `086fc84e8cf1d0b20bd763351d3c44bf7d69832a` plus this action’s owned diff. Seven regressions first failed: four actual stored/deflate/bzip2/lzma overdeclared members, dependency excess delivery, retained public terminal failure and no completed index/CLI publication. Four unchanged underdeclared-size/original-CRC cases already rejected and remain green. The reader now counts delivered bytes, rejects excess before return and requires equality at EOF; README describes the observable stream boundary. All 154 focused ZIP/common-stream/facade/CLI checks, strict mypy and Ruff pass. Separate actual ZIP characterization still returns [0,2] for a two-byte prefix with matching CRC when zipfile clips a six-byte compressed payload; this is retained as an observability limit, not a passing comprehensive underdeclared-tail detector.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-005 — Keep large archive parameter IDs portable

Revision source: `0f21042ddca656194d2a43e4c9c6e0418d8e1d13` plus this action’s owned diff. Before the change, actual legacy-strategy pytest collection produced node IDs of 70082/80097 characters for TAR/7z; default pytest 9.2 already shortened them. Explicit descriptive IDs now keep both default and legacy collections below 108 characters. All 60 affected actual TAR/7z tests and focused Ruff pass. This action changes test metadata only and has characterization/collection evidence rather than a fabricated runtime RED cycle. Native Windows setup/teardown execution remains unverified; the oversized environment-value trigger is removed.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-006 — Read release and example inputs explicitly as UTF-8

Revision source: `95fc30c35735a61b8b8e6cf69aaa55445de58125` plus this action’s owned diff. A new valid UTF-8 TOML case first failed with UnicodeDecodeError under a controlled cp1252-default boundary. Explicit UTF-8 now reads project metadata, shared JSON vectors and README examples independently of the host text locale. All 41 selected locale/release inventory/naming/bundle/installed-example checks pass, including actual native/source-rebuilt consumers; Ruff and strict src/scripts mypy pass. Existing pytest extras/configuration and py7zr>=1.1.4,<1.2 are unchanged. Temporary installed consumers are created only by the existing declared integration fixtures; the tool runtime is not reprovisioned.

The containing action commit records source/tests and this evidence together. Publish/read back the checkpoint before the next action; the final action index retains observed commit identities.

### V-007 — Whole-boundary review and verification

Reviewed the complete diff separately from tests: writable non-truncating synchronization affects only the owned completed SQLite temporary file; explicit source buffering preserves acquisition/cleanup and legal short reads; ZIP size checks precede successful EOF/return without replacing dependency causes; parameter IDs preserve cases; UTF-8 reads preserve declared metadata and example text. No blocking composition finding remains. The public API, accepted contracts, runtime dependency, package version and task/tracking state are unchanged.

Full pytest with strict configuration/markers and coverage passes 705 tests, 95% production statement/branch coverage (1291 statements, 352 branches). All 73 source/test/script files pass Ruff lint/format; strict src/scripts mypy passes all 26 files with --no-native-parser for the known container parser issue. The full suite builds actual wheel/sdist bytes, independently rebuilds the wheel from source, runs both installed variants outside the checkout, executes eight README examples and all supported archive/CLI workflows, and verifies complete native/stable bundle inventory, names, contents and checksums. These are revision validation candidates, not a new published release or artifacts rebuilt from the historical v0.4.0 tag.

Real py7zr 1.1.4 codec/callback/lifecycle/full-format tests run in the provisioned Linux/CPython 3.12.14 environment. Portable Windows fsync-precondition, 128 KiB-default buffering and cp1252-locale regressions are explicitly simulations. Legacy pytest collection confirms short IDs below 108 characters; no native Windows setup/teardown or Python 3.14 execution is inferred. No tool runtime was reinstalled; existing package fixtures own temporary consumer environments.

| Action | Published/read-back source checkpoint |
| --- | --- |
| V-001 | `58a05c80d0a08b190eeaf08df27f3a61326c3ede` |
| V-002 | `e3110f88b6f411886279b4c3628ea17b7511b909` |
| V-003 | `086fc84e8cf1d0b20bd763351d3c44bf7d69832a` |
| V-004 | `0f21042ddca656194d2a43e4c9c6e0418d8e1d13` |
| V-005 | `95fc30c35735a61b8b8e6cf69aaa55445de58125` |
| V-006 | `797a6735da06783ac2a3624cebb9793e86b23f5c` |

The complete diff is limited to accepted source/tests/scripts/README, this active campaign and HANDOFF. Frozen phase/manual reports, original TASKS/hosted closures, pyproject configuration/constraint and existing release/tag remain unchanged. Maintained links, Markdown structure, diff checks and action evidence composition pass. The containing V-007 verification checkpoint must be published/read back before the two-parent merge into refreshed main. Final merge/source publication facts are recorded in the integration boundary and Git; closure follows actual main publication, not this source-check result alone.

## Main integration and closure boundary

Receiving actual default main was refreshed and remained at `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`, the campaign's original creation parent/branch-off. Published incoming verification tip is `ac4bdb13c972ab52a140669bce2d02d784d29d4d`. The complete incoming difference was inspected and contains only the selected review/revision records, repairs, related tests/scripts/README and HANDOFF. No conflicts or product changes relative to that reviewed tip occurred. Original campaign opening remains `7eedb5efdb5e8ce1a6b8ef333a25c9f36c3fb70c`.

Prospective main-merge verification passes all 705 tests, Ruff lint/format over 73 files and strict src/scripts mypy over 26 files. Source/tests/scripts/README/configuration are byte-identical to the reviewed incoming candidate; only active campaign closure evidence and receiving HANDOFF differ. Maintained links/Markdown structure, protected-path checks, original v0.4.0 tag pin and clean conflict state pass. No blocking merged-state finding remains.

The explicit two-parent merge is the campaign completion boundary after supervised main push/readback. Its stored Git parents/message retain the exact merge identity; do not create a post-closure edit to insert the merge's own future SHA. V-001–V-007 and accepted repair scope are complete when that publication succeeds; R-003 remains deferred and unavailable native checks remain recorded limits. Preserve the campaign branch and frozen records, return on main and stop without version/release work.
