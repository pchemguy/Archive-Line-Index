# Project handoff

Checkpoint: The requested testing closure, comprehensive code/docs review and important repairs, review closure, patch bump and GitHub release are complete. Work returns to main with no active campaign or pending release operation. Preserve all closed campaign/phase/manual/preparation records and existing tags/releases.

## Campaign outcomes

Testing campaign 004 was integrated and published as 544c11280b807fd03c158023c5563dda5d453e34. Comprehensive campaign 005 was integrated and published as b4ca1d931d7c1c3da5e07e23f4bcaf185aae7ab5. Its [review](reviews/005_544c112-code-docs/REVIEW-REPORT.md) and [revision results](reviews/005_544c112-code-docs/REVISION-REPORT.md) are frozen. All three important findings were verified; minor test-placement-map recommendation R-004 remains deferred. No production defect was confirmed in that review. Delivered repairs cover version-aware integration checks, pre-write symlink staging rejection and complete build/Hatchling test prerequisites with matching README guidance.

The subsequent 0.4.1 full release run exposed one remaining hardcoded unit version assertion (1 failed, 712 passed). The release commit corrects it to validate the established version shape and uses UTF-8 metadata reads. Four focused cases pass; final exact pytest -vv with coverage passes all 713 tests (478 unit, 235 integration) in 33.08 seconds at 95% production statement/branch coverage. Ruff lint/format pass for 74 files and strict mypy for 26 source/script files with --no-native-parser. The earlier clean declared-extras environment also passed the complete suite.

## Published release

[Archive Line Index v0.4.1](https://github.com/pchemguy/Archive-Line-Index/releases/tag/v0.4.1) is published stable/latest, GitHub release ID 434318201. The lightweight tag and default-branch release commit both identify eb67b15da59f2b9e130ad02e90be0cc3c9d04d9d; its exact body matches root RELEASE-NOTES.md and the hosted release body. This later outcome-only checkpoint does not move that tag or rebuild/replace its assets. Previous release v0.4.0 remains pinned at 7ee4afc200c7fded93880397128b0a9e217f3c52.

Complete Git coverage since v0.4.0 includes the previously unreleased buffering/ZIP/SQLite/UTF-8 fixes, reliable pytest execution and this review's release/test-tooling repairs. Source/version/installation/notes agree at 0.4.1. Exact-source verification compared all 136 packaged tracked files, rebuilt the wheel from the source distribution and exercised both isolated installed variants. Each variant passed eight README examples, six plain CLI cases and 37 archive cases. Both native and source-rebuilt wheel hashes matched in this execution; no broader reproducible-build certification is implied.

| Hosted artifact | Bytes | SHA-256 |
| --- | --- | --- |
| archive-line-index-source.zip | 227903 | 616cf5a56d5c3f4a9479337e772e25c583a51b1bbfe081a511aec5075eb6305c |
| archive-line-index-wheel.zip | 38508 | 01533b7a856793109dcf800ae4710bf47a72822cc696e5c534bf38dbfac935b6 |
| SHA256SUMS | 191 | b5da6bde9d955118b1ae8574f1a42ddcd40ca0ab636edbfaceab33018e30ae2e |

Native and outer inventories passed metadata/content/source/checksum validation and the independent version-free naming gate before tagging. The draft was complete before publication. Hosted tag/source, exact notes, stable/latest selection, complete asset names/sizes/digests and every tag-specific/latest downloaded byte stream were read back and verified against these hashes. SHA256SUMS matches byte-for-byte. The workflow-owned ignored .release-highlights.md checkpoint was removed only after successful published-body consumption; root release notes remain retained.

## Limits and stop

Actual execution is Linux/CPython 3.12.14 with py7zr 1.1.4. Native Windows/macOS/Python 3.11/3.14/big-endian execution remains unverified; targeted simulations do not certify those hosts. Existing cooperative 7z cancellation, observable-only ZIP integrity and independent paired-output publication limits remain documented. Minor R-004 is the only deferred finding in campaign 005. Publish/read back this outcome commit on main, then stop for the next user instruction. Markdown prose/list items remain unwrapped.
