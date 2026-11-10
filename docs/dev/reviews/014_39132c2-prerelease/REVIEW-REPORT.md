# Archive Stream v0.5.3 prerelease review report

Campaign `014_39132c2` opened from the published CLI logging campaign tip `39132c2089c63808a2df5c914554b27d504b5f94`. [Review plan](REVIEW-PLAN.md) defines candidate identity, review units and return target.

## U-01 critical README review

Reviewed the product introduction, install and upgrade paths, first runnable stream example, indexing and output ownership, source restrictions, logging, demos and contract navigation. The stream-first order and independent index workflow fit the current project. Both installed-artifact documentation tests ran all nine Python examples.

| ID | Finding and consequence | Proposed correction and recheck |
| --- | --- | --- |
| F-001 | Important, high confidence, consumer guidance. The progress section mixes CLI interpretation with application configuration, and readers must assemble the new three-line pattern from prose. The sentence about extra extraction workers does not clearly attribute the restriction to logging, although the 7z adapter owns a worker. | Lead with the CLI's stderr output, show periodic and completion records together, distinguish rounded complete-buffer progress from exact bytes and elapsed time, and give the quiet-mode control before application configuration. Verify the transcript against a deterministic real CLI invocation. |
| F-002 | Important, high confidence, release handoff. The published v0.5.2 wheel and the checkout differ in their logging behavior, but the installation and development commands still pin v0.5.2. Leaving the current links would send readers to the previous formatter. | Align metadata, installation, artifact commands and release notes with v0.5.3 at the release boundary. Verify actual tagged bundle and checksum downloads. |

## U-02 comprehensive product and artifact review

Traced the active project, design, public API and specification contracts through the source, test ownership, checkout demos and packaging. Since v0.5.2 the production delta is limited to the scanner observer and API documentation. Reviewed buffer-size arithmetic, promotion and rounding across supported offset ranges, monotonic timing, disabled logging, validated EOF, failure and cleanup, and the CLI's stdout/stderr and independent publication boundaries. Rechecked unchanged format detection, plain/ZIP/TAR/7z streaming, line offset semantics, persistence and CLI behavior with the full suite and six-format demo parity. All 773 tests passed at 95% coverage on Linux/CPython 3.12.14. Ruff and strict mypy passed. Native Windows CMD and macOS remain unverified.

Reviewed the actual native candidates and source-rebuilt consumers, typed/public import and console mappings, supported runtime dependency, exclusion rules, checksums and stable bundles. There is no tracked Actions publisher. Direct GitHub draft, verified upload and publication match the established route. A deterministic CLI run yielded the intended three-line transcript for F-001.

| ID | Finding and consequence | Proposed correction and recheck |
| --- | --- | --- |
| F-003 | Important, high confidence, release checker defect. A real wheel with `archive-line-index : archive_stream.cli:main` passed the validator and received checksums because its INI parser accepts colon delimiters. Python's distribution entry-point reader rejected the same declaration with `TypeError`. | Require the equals delimiter in wheel entry-point metadata and add a failing case to the artifact suite. Recheck valid native, bundled and installed artifacts. |
| F-004 | Minor, high confidence, design consistency. The decomposition and line-index contract still describe one completion event and omit elapsed time where they summarize the scanner's current output. | Align both summaries with the canonical progress contract and retain the distinction from source cleanup and index publication. |

F-001 through F-004 are in the requested repair scope. Exact-source and hosted release gates are pending.
