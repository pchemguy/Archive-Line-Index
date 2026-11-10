# Project handoff

Archive Stream prerelease campaign `012_2fda1e4` is closed at merge `8c6ccc6202f8a7dfe22102eb52bb55a04013f9e1`. The [review report](reviews/012_2fda1e4-prerelease/REVIEW-REPORT.md) and [revision report](reviews/012_2fda1e4-prerelease/REVISION-REPORT.md) retain the four findings and campaign evidence. F-002 is verified by the current README and the matching hosted release downloads.

[Archive Stream v0.5.2](https://github.com/pchemguy/Archive-Stream/releases/tag/v0.5.2) is published stable and verified as latest. Release ID `440082586` and lightweight tag `v0.5.2` identify release commit `5b8caaf1baf67f72f7d3a5916bff95ca7b1bf1d2` on remote `main` first-parent history. The release commit body, retained [release notes](../../RELEASE-NOTES.md), and actual GitHub body match byte-for-byte.

The exact release source passed 760 tests with 95% coverage on Linux with CPython 3.12.14. Native and source-rebuilt wheels each passed all nine README examples, six plain CLI cases, 37 archive cases, and installed runtime checks with py7zr 1.1.4. All 170 tracked source-distribution files compared byte-for-byte with the release commit. The prospective campaign merge passed 42 focused tests, correcting the count of 41 in its message. Checkout CLI/API parity passed on all six formats. Native Windows CMD and macOS execution remain unverified.

| Release asset | SHA-256 |
| --- | --- |
| archive-stream-source.zip | 07eb9e5af26b956b9dbdf1fe99ef0a67bfa8634238913244856b0408e44d9fa8 |
| archive-stream-wheel.zip | aba5878b0e0c35062ad89261ff1b18630ae0f416180563053edf2981fcdf47a9 |
| SHA256SUMS | 3e1a90d181cd76fb3188a52f7a9cbc72c414d32c806a03ecd998e2e8bcd277a4 |

All tag-specific and latest download bytes match the verified local inventory. The published body consumed the internal highlights checkpoint. No campaign or release work is pending at this checkpoint.
