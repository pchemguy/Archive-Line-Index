# Project handoff

Documentation revision campaign `015_132a8e7` delivered the [API reference](../API_REF.md) and README link. The [revision report](reviews/015_132a8e7-docs/REVISION-REPORT.md) records the 774 passing tests and streaming example checks.

The [v0.5.3 prerelease campaign](reviews/014_39132c2-prerelease/REVISION-REPORT.md) closed at nested merge `40e89e1ccdda9f97b27316a9eaf194dc5303bc28`. The [CLI logging parent campaign](reviews/013_833560e-cli-logging/REVISION-REPORT.md) closed on `main` at merge `3e346fce534c0ef7b57ecb31646023d96a9de20f`. F-002 is verified by the current README and the matching public v0.5.3 downloads.

[Archive Stream v0.5.3](https://github.com/pchemguy/Archive-Stream/releases/tag/v0.5.3) is published stable and verified as latest. Release ID `440264432` and lightweight tag `v0.5.3` identify `d5f5e344750515e4145785cdcc6c11ad247a7f6a` on remote `main` first-parent history. The release commit body, [retained notes](../../RELEASE-NOTES.md), and hosted release body match byte-for-byte.

The exact release source passed 774 tests with 95% coverage on Linux with CPython 3.12.14. The native and source-rebuilt wheels each passed all nine README examples, six plain CLI cases, 37 archive cases and runtime checks using py7zr 1.1.4. All 176 tracked files in the source distribution matched the tagged source. The merged checkout demos agreed for six formats. Native Windows CMD and macOS execution remain unverified.

| Release asset | SHA-256 |
| --- | --- |
| archive-stream-source.zip | bf8f10dd1adfbf0e38acbfaa65da631cb3d37eb88624fd146aa588423793aa0a |
| archive-stream-wheel.zip | 50574fe1de62458693c7c2a728d1b40d4e76217fb98ab043ad6670f03fa11b65 |
| SHA256SUMS | 1fbe3b20fe0e9cfff2cb96a189d49bde7d77e3e05bdc00d812c342aedb5d9dbb |

All three tag-specific and all three latest downloads match the verified local bytes. The hosted body consumed the internal highlights checkpoint. No campaign or release work is pending.
