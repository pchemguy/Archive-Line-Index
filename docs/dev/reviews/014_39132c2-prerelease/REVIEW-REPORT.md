# Archive Stream v0.5.3 prerelease review report

Campaign `014_39132c2` opened from the published CLI logging campaign tip `39132c2089c63808a2df5c914554b27d504b5f94`. [Review plan](REVIEW-PLAN.md) defines candidate identity, review units and return target.

## U-01 critical README review

Reviewed the product introduction, install and upgrade paths, first runnable stream example, indexing and output ownership, source restrictions, logging, demos and contract navigation. The stream-first order and independent index workflow fit the current project. Both installed-artifact documentation tests ran all nine Python examples.

| ID | Finding and consequence | Proposed correction and recheck |
| --- | --- | --- |
| F-001 | Important, high confidence, consumer guidance. The progress section mixes CLI interpretation with application configuration, and readers must assemble the new three-line pattern from prose. The sentence about extra extraction workers does not clearly attribute the restriction to logging, although the 7z adapter owns a worker. | Lead with the CLI's stderr output, show periodic and completion records together, distinguish rounded complete-buffer progress from exact bytes and elapsed time, and give the quiet-mode control before application configuration. Verify the transcript against a deterministic real CLI invocation. |
| F-002 | Important, high confidence, release handoff. The published v0.5.2 wheel and the checkout differ in their logging behavior, but the installation and development commands still pin v0.5.2. Leaving the current links would send readers to the previous formatter. | Align metadata, installation, artifact commands and release notes with v0.5.3 at the release boundary. Verify actual tagged bundle and checksum downloads. |
