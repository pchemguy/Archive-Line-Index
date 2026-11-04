# Project handoff

Testing campaign 004 and comprehensive code/docs campaign 005 are closed and published on main. Latest integration b4ca1d931d7c1c3da5e07e23f4bcaf185aae7ab5; [review](reviews/005_544c112-code-docs/REVIEW-REPORT.md) and [revision results](reviews/005_544c112-code-docs/REVISION-REPORT.md) are frozen. All three important findings are verified; minor layout recommendation R-004 remains deferred. Merged verification passed 713 tests; clean declared-extras verification passed 713 tests with 95% coverage. Ruff lint/format and strict mypy pass. Native Windows/macOS/Python 3.11/3.14/big-endian execution remains unverified.

## Active release operation

The human authorized patch release 0.4.1 after campaign closure. Actual repository default is main, confirmed through hosted metadata. Previous release v0.4.0 peels to 7ee4afc200c7fded93880397128b0a9e217f3c52; complete Git inventory through the integration above and net source/config/docs changes have been analyzed for release highlights. Root RELEASE-NOTES.md contains the finalized complete message; version metadata and current README installation/check commands now use 0.4.1. Public APIs/runtime constraints remain unchanged.

Verify this complete release source, build and check the actual candidate inventory, create a direct-main release commit whose exact body is RELEASE-NOTES.md, publish/read back that commit, rebuild/verify the exact committed source and installed consumers, then tag and publish the GitHub release with archive-line-index-wheel.zip, archive-line-index-source.zip and SHA256SUMS. Read back the tag/source/body/inventory, downloaded bytes and latest links before claiming completion. Preserve closed campaign records and the original tags/releases; never move the release tag to a later outcome-report commit. This checkpoint records preparation, not completed hosted publication.


## Release-source verification

The first full 0.4.1 run exposed one remaining fixed-version assertion in tests/unit/test_package.py (1 failed, 712 passed). That test now checks the established three-component version shape and console mapping rather than pinning 0.4.0, and reads metadata as UTF-8. Its four focused cases pass; the corrected exact pytest -vv --cov=archive_line_index --cov-report=term-missing run passed all 713 tests in 33.08 seconds at 95% coverage. Ruff lint/format (74 files) and strict mypy (26 source/script files, --no-native-parser) pass. This bounded release-verification correction is authorized by the release/important-fix request; closed campaign records remain unchanged.

This containing direct-main release commit includes only version/install/notes/continuity/ignore changes and that test correction. Its body exactly matches the final release notes. After its source publication/readback, rebuild and verify the exact committed packages and hosted inventory before creating the tag; hosted publication remains pending.
