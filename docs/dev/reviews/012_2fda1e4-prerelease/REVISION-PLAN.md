# Archive Stream v0.5.2 revision plan

Campaign `012_2fda1e4` integrates into `main`. The user authorized all four [review findings](REVIEW-REPORT.md) for repair, followed by preparation, patch bump, closure and release.

| Action | Findings | Delivery and verification |
| --- | --- | --- |
| R-001 | F-001, F-003, F-004 | Make the primary example read a compressed payload in blocks through EOF. Clarify backend scope and checkout demo navigation. Validate native wheel and sdist console declarations. Reproduce rejected artifacts and run both installed README variants, the full suite, tools, and demo parity. |
| R-002 | F-002 | Prepare release notes, bump to 0.5.2, and align README version-specific package and verification instructions. Close via a verified two-parent merge into `main`. Finalize release notes and install links on the default branch, rebuild from the exact release commit, verify the two native packages and complete hosted bundle inventory, then publish and verify the stable GitHub release. |

The v0.5.1 release retains its original package identity. Existing indexing command, stream behavior, and index file contracts carry forward. Release assets are `archive-stream-source.zip`, `archive-stream-wheel.zip`, and `SHA256SUMS`.
