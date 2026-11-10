# Archive Stream v0.5.2 revision report

## R-001 README and artifact repairs

F-001 and F-003 are verified. The first README workflow now opens a deflated ZIP, reads bounded blocks through validated EOF, and hashes them incrementally. The backend introduction defines the compressed-TAR boundary and identifies its index examples. The checkout demo link resolves to the repository tree. Both installed artifact variants executed all nine README examples. The six Alphanum CLI/API comparisons passed.

F-004 is verified. Native and bundle validation now require the wheel console script and the source declaration to match the selected project's scripts before writing checksums. The absent, stale-wheel, and stale-source regression cases all failed before the repair and passed after it. The full repaired Linux suite passed 760 tests with 95% coverage. Ruff lint and format and strict mypy passed. Native Windows/macOS execution remains unverified.

F-002 will be verified at the release boundary after version, notes, asset metadata and download checks.

## R-002 version and release preparation

The release version is 0.5.2, with release notes covering the renamed distribution, retained indexing command, README repairs, demos, and console-script verification. Updated version-specific artifact check commands. The v0.5.2 candidate passed native and stable-bundle checks and five metadata, installed-consumer and README test cases. F-002 preparation passed locally. The final release step owns the README download links and confirmation of the corresponding hosted assets.

The user requested closure before publication. The opening commit is `d0bfa38` and the receiving `main` baseline is `2fda1e405fac8df69e72068eee4d5edc7f05487c`. Close through a verified two-parent merge, then build and verify the exact default-branch release commit before tag and asset publication.
