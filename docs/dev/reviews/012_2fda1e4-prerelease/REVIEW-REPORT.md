# Archive Stream v0.5.2 prerelease review report

Campaign `012_2fda1e4` opened from verified remote `main` at `2fda1e405fac8df69e72068eee4d5edc7f05487c`. [Review plan](REVIEW-PLAN.md) owns scope, unit order and candidate boundaries.

## U-01 critical README review

Reviewed the opening promise, section order, installation and upgrade, stream and index workflows, backend coverage, demo, integration links and development commands against the public contract and the checkout. Both installed-artifact tests executed all nine Python examples successfully. The README establishes the right product priority and separates payload reads, line-index construction and file persistence. Its format, ownership and index output claims agree with the contracts, subject to the qualifications below.

| ID | Finding and consequence | Proposed correction and objective recheck |
| --- | --- | --- |
| F-001 | Important, high confidence, consumer guidance. The first streaming example performs a predetermined sequence of reads on a ZIP fixture created without compression. It does not demonstrate the positive-size loop that callers need for short reads and validated EOF. | Use an actual compressed fixture and a block loop that consumes through EOF. Verify exact bytes and execute the example against both installed artifacts. |
| F-002 | Important, high confidence, release readiness. Installation describes checkout use only and directs release readers to v0.5.1, which installs the old distribution. Artifact verification commands also specify v0.5.1. | Supply the v0.5.2 wheel/source/checksum instructions and matching verification commands with the release commit. Verify that the actual tag assets, native names and downloadable checksums agree. |
| F-003 | Minor, high confidence, composition and scope. The general integration summary is followed by repeated index-only illustrations under each source backend. The standalone stream discussion omits the supported distinction between raw gzip/bzip2/xz and compressed TAR. The demo link is relative to a checkout-only directory missing from the source distribution. | Keep backend-specific caveats and existing executable index cases, label them as such, state that compressed TAR variants require a TAR payload and point readers to the checkout demo on GitHub. Verify the corresponding contract, links and installed examples. |
