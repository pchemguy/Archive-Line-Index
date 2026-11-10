# Archive Stream v0.5.2 revision report

## R-001 README and artifact repairs

F-001 and F-003 are verified. The first README workflow now opens a deflated ZIP, reads bounded blocks through validated EOF, and hashes them incrementally. The backend introduction defines the compressed-TAR boundary and identifies its index examples. The checkout demo link resolves to the repository tree. Both installed artifact variants executed all nine README examples. The six Alphanum CLI/API comparisons passed.

F-004 is verified. Native and bundle validation now require the wheel console script and the source declaration to match the selected project's scripts before writing checksums. The absent, stale-wheel, and stale-source regression cases all failed before the repair and passed after it. The full repaired Linux suite passed 760 tests with 95% coverage. Ruff lint and format and strict mypy passed. Native Windows/macOS execution remains unverified.

F-002 will be verified at the release boundary after version, notes, asset metadata and download checks.
