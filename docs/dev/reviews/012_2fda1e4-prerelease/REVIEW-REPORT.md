# Archive Stream v0.5.2 prerelease review report

Campaign `012_2fda1e4` opened from verified remote `main` at `2fda1e405fac8df69e72068eee4d5edc7f05487c`. [Review plan](REVIEW-PLAN.md) owns scope, unit order and candidate boundaries.

## U-01 critical README review

Reviewed the opening promise, section order, installation and upgrade, stream and index workflows, backend coverage, demo, integration links and development commands against the public contract and the checkout. Both installed-artifact tests executed all nine Python examples successfully. The README establishes the right product priority and separates payload reads, line-index construction and file persistence. Its format, ownership and index output claims agree with the contracts, subject to the qualifications below.

| ID | Finding and consequence | Proposed correction and objective recheck |
| --- | --- | --- |
| F-001 | Important, high confidence, consumer guidance. The first streaming example performs a predetermined sequence of reads on a ZIP fixture created without compression. It does not demonstrate the positive-size loop that callers need for short reads and validated EOF. | Use an actual compressed fixture and a block loop that consumes through EOF. Verify exact bytes and execute the example against both installed artifacts. |
| F-002 | Important, high confidence, release readiness. Installation describes checkout use only and directs release readers to v0.5.1, which installs the old distribution. Artifact verification commands also specify v0.5.1. | Supply the v0.5.2 wheel/source/checksum instructions and matching verification commands with the release commit. Verify that the actual tag assets, native names and downloadable checksums agree. |
| F-003 | Minor, high confidence, composition and scope. The general integration summary is followed by repeated index-only illustrations under each source backend. The standalone stream discussion omits the supported distinction between raw gzip/bzip2/xz and compressed TAR. The demo link is relative to a checkout-only directory missing from the source distribution. | Keep backend-specific caveats and existing executable index cases, label them as such, state that compressed TAR variants require a TAR payload and point readers to the checkout demo on GitHub. Verify the corresponding contract, links and installed examples. |

## U-02 comprehensive product and release review

Compared the complete current product against the project, architecture, decomposition, public and internal API designs, seven behavioral contracts and physical layout. Reviewed capability boundaries and test coverage for detection and registry dispatch, bounded read and retained failure, ZIP/TAR/7z adapter completion, cooperative 7z cancellation and backpressure, scanner LF/BOM/EOF and logging, both persistence formats, destination publication and CLI statuses. The production diff from v0.5.1 changes package paths and scanner logger qualification without changing these algorithms. Reviewed the checkout demo, packaging ownership and release instructions. There is no tracked Actions publisher. The direct GitHub draft/upload route fits the repository.

On Linux with CPython 3.12.14, all 757 baseline tests passed at 95% coverage, including clean wheel and source-rebuilt wheel consumers, archive corruption and cancellation, publication races, both CLI forms plus the imported callable, and release inventory fault cases. Ruff lint/format passed for 78 files, strict mypy passed for 26 source/script files, and all six demo inputs produced matching CLI and API outputs. Native Windows/macOS were unavailable. The 7z dependency's cooperative cancellation and internal allocation limits and ZIP's observable validation boundary are documented.

| ID | Finding and consequence | Proposed correction and objective recheck |
| --- | --- | --- |
| F-004 | Important, high confidence, artifact verification defect. The native validator checks package bytes and core metadata but omits the wheel's declared console script. A real wheel repacked with `archive-line-index = archive_line_index.cli:main` passed native validation and checksum generation even though that import was removed. The installed tests catch an incorrect entry point, while the standalone native and bundle gates could approve an independently supplied broken package. | Validate the wheel console-script mapping and the embedded source declaration against the selected project metadata before writing checksums. Reproduce absent/stale metadata on synthetic candidates, then verify actual native and bundled artifacts and clean installs. |

Proceed with F-001 through F-004 under the requested repair authority. Readiness remains conditional on those rechecks and the exact-source release and hosted asset gates.
