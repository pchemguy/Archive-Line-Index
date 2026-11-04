# Archive Line Index delivery plan

## Objective and strategy

Deliver the complete [PROJECT](PROJECT.md) scope through five useful increments conforming to [SPEC](SPEC.md), its contracts and the accepted [component/API design](DECOMPOSITION.md). The first usable product streams and indexes a plain file through an installed library. Persistence and the paired-output CLI follow; standard-library archives extend that workflow; the bounded threaded 7z adapter completes archive coverage.

This sequence makes the scanner, ownership rules and installed-library path usable before introducing file publication or producer concurrency. Every increment retains working prior behavior. The complete specification remains the intended system; intermediate versions expose and document only their delivered capabilities, without presenting planned entry points or formats as implemented. Recognized archive candidates without an implemented adapter are rejected explicitly rather than indexed as plain bytes.

| Phase | Integrated outcome | Planned package version | Prerequisite |
| --- | --- | --- | --- |
| 1 — Plain-file library | Standalone plain payload streaming and exact LF/BOM line offsets through installed public APIs | 0.1.0 | Accepted preparation integrated and published; implementation range selected |
| 2 — Paired persistence and CLI | Persist/reload either index format and index one plain target through console, module or imported CLI, producing both outputs | 0.2.0 | Phase 1 reviewed, integrated and its GitHub release published |
| 3 — ZIP and TAR workflows | The same public APIs and CLI work with ZIP, TAR and required compressed-TAR variants | 0.3.0 | Phase 2 reviewed, integrated and its GitHub release published |
| 4 — 7z and complete-system delivery | Bounded 7z streaming/indexing and paired CLI outputs, with complete accepted-scope evidence | 0.4.0 | Phase 3 reviewed, integrated and its GitHub release published |
| 5 — Lightweight progress logging | Five-second cumulative indexing bytes through standard logging, scoped CLI INFO/stderr and suppression, with preserved library configuration/semantics | 0.5.0 | Phase 4 reviewed/integrated/released; accepted feature preparation and tracking ready |

After each implementation phase is complete, verified and integrated into the default branch, create and publish a GitHub release for its package version, tagged `v0.1.0` through `v0.5.0` respectively. Each release includes release notes and explicitly attached source-distribution and wheel artifacts built from the exact tagged source, with matching metadata and SHA-256 checksums. Automatic GitHub source links do not substitute for the attached source distribution.

## Phase 1 — Plain-file library

**Outcome:** A Python caller can install the package, stream a plain file or scan a readable binary source, and obtain exact canonical offsets without archive or persistence support.

| Milestone | Delivered capability and exit evidence |
| --- | --- |
| 1.1 — Plain content access | Implement source normalization, bounded detection, shared errors, the backend reader and plain adapter behind the common stream. Demonstrate byte-identical reads, readinto byte capacity, inclusive limits, validated EOF, retained failure and deterministic close. Reader doubles exercise late failures without requiring archive libraries. Configured checking tools must be runnable for this capability. |
| 1.2 — Canonical line indexing | Implement the offset model and generic scanner. Demonstrate every line/BOM example, arbitrary legal short reads, invalid result rejection, signed-range boundaries, caller ownership and long-line bounded scanning. Use the same model validation that persistence will consume. |
| 1.3 — Installed source-based indexing | Compose source opening with scanning, expose the delivered public surface and establish valid packaging/version metadata. Build and install the wheel outside the checkout; demonstrate stream-only, direct-scan and source-based workflows plus failure cleanup. Supply accurate installation/API examples and a rebuildable source distribution. |
| 1.4 — Phase review | Review the complete plain-file outcome and cross-milestone interactions, run applicable regressions and retain phase evidence before integration. |

**Scope and exclusions:** Deliver API/stream/index contracts for plain input. Persistence, CLI execution and archive adapters are not this version's delivered capabilities. The public library foundation includes the actual validation and resource guarantees needed for safe standalone use; the first phase is not merely an importable skeleton.

**Exit:** IDX-01–06 are satisfied; API-01–05 and STR-01–06 are satisfied for delivered operations and plain/controlled-reader cases. SYS-02–06 and SYS-10–12 have phase-scoped evidence. Archive-specific, persistence and CLI portions remain scheduled below. Demonstrate an installed plain-file index result with correct sentinel/line ranges; that working capability allows the human to continue, amend, simplify or stop before selecting more implementation.

## Phase 2 — Paired persistence and CLI

**Outcome:** A caller can independently store/load a canonical array, or index one plain target once into SQLite and raw outputs through the installed CLI and its importable entry point.

| Milestone | Delivered capability and exit evidence |
| --- | --- |
| 2.1 — Independent index persistence | Implement completed-array validation consumers, temporary/publication ownership and both SQLite/raw readers and writers. Demonstrate exact cross-format round trips, self-contained SQLite completion, little-endian encoding, existing-destination protection, publication-time exclusive creation, replacement and pre/post-publication failure outcomes. |
| 2.2 — Importable paired-output command | Implement the CLI adapter using existing index/persistence providers. Demonstrate one target, one scan, two sequential writes, default input-directory/stem naming, explicit shared stem, overwrite preflight for both paths and source aliases, integer statuses, help/usage and accurate partial-publication diagnostics. Imports perform no CLI work. |
| 2.3 — Installed command workflow | Wire the console entry point and guarded module runner to the same callable, package them and document their use. Demonstrate all three invocation paths outside the checkout, generated SQLite/raw equivalence, spaces/hyphen-prefixed paths, protected outputs, failure/interruption cleanup and no development/runtime-tool leakage. |
| 2.4 — Phase review | Review the persistence/CLI composition and preserved Phase 1 behavior, run scoped end-to-end and publication-failure checks and retain phase evidence before integration. |

**Scope and exclusions:** Complete PER-01–07 and plain-input CLI-01–06, including both outputs and independently usable library persistence. Archive CLI cases remain for their adapter phases. Paired CLI output has no cross-file transaction; already completed publication is retained and reported when the later write fails.

**Exit:** SYS-07–11 and SYS-13 have evidence for plain input; API and stream/index regressions remain green. An installed single-target command produces both expected files, and their independent readers reconstruct the same array. At this demonstration the human can judge the minimal command/naming workflow and choose the next range or an amendment; the demonstration does not authorize automatic scope changes.

## Phase 3 — ZIP and TAR workflows

**Outcome:** Users apply the existing stream, index and paired CLI workflows to ZIP and sequential TAR, including gzip, bzip2 and xz TAR variants.

| Milestone | Delivered capability and exit evidence |
| --- | --- |
| 3.1 — ZIP source integration | Add the ZIP adapter through existing detection/reader boundaries. Demonstrate valid/empty/nested members, full-list structure checks, exposed special entries and encryption rejection, unconventional/conflicting suffixes, CRC/truncation failures and limits. Verify both standalone streaming and composed indexing/paired CLI use with actual ZIP files. |
| 3.2 — Sequential TAR integration | Add TAR and required compression filters. Demonstrate correct single-member payloads, trailing exposed-entry validation, available header/trailer integrity checks, invalid compressed plain inputs and all failure/cleanup paths. Recheck equivalent plain/ZIP/TAR corpora and installed CLI/persistence behavior without changing scanner or storage semantics. Refresh artifacts and format examples. |
| 3.3 — Phase review | Review both standard-library adapter families, preserved earlier workflows and installed artifacts; run cross-format regressions and retain phase evidence before integration. |

**Scope and exclusions:** ARC-01–05, SYS-01 and relevant stream/CLI conditions apply to the delivered plain/ZIP/TAR set. 7z integration, its queue/thread lifecycle and dependency-suitability evidence remain for Phase 4. Neither the scanner nor CLI acquires format-specific algorithms.

**Exit:** Equivalent payloads across the delivered formats yield identical bytes, offsets and paired persistence. A TAR with an invalid trailing member cannot yield a completed index. Malformed/corrupt sources do not yield success summaries or output publication after an indexing failure. Demonstrations of ZIP and compressed-TAR CLI indexing support the human's next range/adjustment decision.

Two delivery milestones are intentional: ZIP's random-access member metadata and TAR's sequential/trailing-validation mechanics are distinct cohesive outcomes. A separate generic integration milestone would duplicate their required end-to-end exits and the phase review. Both milestones include actual consumer integration, not only backend construction.

## Phase 4 — 7z and complete-system delivery

**Outcome:** 7z becomes an actual supported source for standalone streaming, index construction and paired CLI execution, completing the accepted functionality.

| Milestone | Delivered capability and exit evidence |
| --- | --- |
| 4.1 — Bounded 7z streaming | Implement the callback writer, finite transport and one outer extraction worker within the 7z adapter. Select and record a compatible dependency constraint through real callback/codec evidence. Demonstrate byte fidelity, empty payload, backpressure, terminal outcomes, active early close and resource ownership through the common public stream. No full extraction/materialization fallback is permitted. |
| 4.2 — 7z indexing and complete distribution | Complete structure/error/limit and cancellation integration with source-based indexing and the existing paired CLI. Demonstrate dependency failures, full-queue cancellation, no surviving owned thread after successful close and unchanged line/persistence semantics. Build/install the full package, update complete usage/API guidance and remove the temporary legacy reference from root AGENTS when reimplementation is complete. |
| 4.3 — Phase and final review | Review the complete accepted system, run integrated regressions and installed-artifact checks, aggregate remaining findings/TODOs in the final implementation report and retain phase/final evidence before integration. |

**Exit:** All 49 baseline Phase 4 SPEC acceptance conditions have applicable evidence, with actual dependency versions, host capabilities and unavailable native execution identified. Existing milestones' evidence can be retained when still current, while changes trigger affected regressions. Full-scope public exports, formats, errors, lifecycles and both CLI artifacts match their contracts. The legacy reference is absent from active agent guidance, and product documents contain no migration narrative.

Two delivery milestones keep the adapter's bounded streaming/ownership risk distinct from its completed indexing/CLI and distribution outcome. Final verification is the dedicated phase review, not a backlog milestone containing unplanned features. A dependency that cannot satisfy callback fidelity or cooperative cleanup blocks the affected 7z completion and requires a design/dependency decision before proceeding; it does not retroactively erase the usable Phase 3 package.

## Cross-cutting gates and dependencies

- **Contract-first work:** Accepted API/model/contract owners are prerequisites for their consumers. TASKS must allocate localized test-first work, implementation and professional documentation together. Numeric internals and dependency constraints may be refined within existing contract limits with evidence; material surface/behavior changes return to the owning document checkpoint.
- **Continuous verification:** Use configured Ruff formatting/lint, strict mypy, pytest and coverage measurement alongside focused functional/resource checks. Each capability includes its errors and cleanup rather than deferring robustness to the last phase. Native platform checks run where available; unavailable target-native facilities are reported without inventing a completion blocker. Installed wheels and source-distribution rebuilds are verified on the actual host.
- **Milestone exits:** Every delivery milestone includes code review, focused tests/regressions, correction of contract/blocking defects, documentation and durable boundary evidence. TASKS assigns a separate milestone review task only when the milestone has at least four implementation tasks and the phase has at least two delivery milestones; otherwise the final implementation task owns those obligations.
- **Phase exits:** Each phase has exactly one final dedicated review milestone containing one review/testing/report task. It starts after delivery milestones and enabled tracking closures complete. A phase integrates only after its review, applicable artifacts and exits pass; verify/publish the merged result before an authorized successor starts. Partial ranges push and pause without integrating an incomplete phase.
- **Tracking:** Project policy enables GitHub tracking. Activate only the eligible phase's label, milestones and task issues before its execution, with association/readback and evidence-based closure. Local PLAN/TASKS contain the full intended hierarchy; preparation does not create future-phase hosted objects.
- **Packaging and feedback:** Each phase's version/artifacts and documented capabilities agree. Demonstration feedback informs the human's decisions but adds no approval pause inside an already authorized range unless a material decision/blocker requires it. Implementation remains bounded by the human's selected range.

## Phase release gate

The final phase review prepares verified package candidates and release notes for that phase’s delivered scope, including installation/use instructions, checks performed and material evidence limits. After verified integration, finalize and verify the release commit on the actual default branch, rebuild/verify the source distribution and wheel from that exact source, publish/read back the corresponding version tag, and publish the GitHub release with both explicit wheel/source bundles and `SHA256SUMS`. Verify the hosted notes, tag target, asset names and downloaded bytes against the local inventory before declaring release completion or starting an authorized successor phase. A partial implementation range does not trigger a phase release.

Every hosted release artifact has a stable version-free name. The complete expected inventory is `archive-line-index-wheel.zip`, `archive-line-index-source.zip` and `SHA256SUMS`. The wheel/source bundles each contain exactly one valid native package with its ecosystem-required internal filename and matching version metadata. Native packages are private build inputs and bundled payloads; only the stable outer bundles and checksum file are hosted assets. Validate the entire flat hosted inventory against the independent naming contract and shared notation vectors, with no extension allowlist or matching-manifest exemption. Verify native metadata/source equality, bundle checksums and downloaded-byte identity before publication is complete. PyPI publication is not part of the phase release policy.

## Implementation ownership

[Layout](layout.md) assigns physical ownership, and [TASKS](TASKS.md) defines executable units and task-level dependencies within these phase/milestone boundaries. [PLAN review](PLAN-REVIEW-REPORT.md) records strategy and placement conformance. Source/test allocation, the executable checklist and its status retain their respective owners.

## Phase 5 — Lightweight progress logging

Deliver standard named-logger observations of cumulative uncompressed indexing bytes at five-second chunk-boundary intervals and a final validated-scan total. Library callers configure their handlers; CLI default INFO progress is visible on stderr without altering root/parent settings or accumulating handlers. --log-level WARNING restores quiet progress behavior. Preserve all earlier line/archive/persistence/resource semantics and public signatures; do not add compressed counters, per-line events, workers, a custom framework or progress bars.

Delivery milestone 5.1 contains three meaningful outcomes: scanner observation, CLI configuration and installed/documented distribution behavior. Its final implementation task owns whole-milestone review/report because no standalone review is justified for three tasks. Review milestone 5.2 contains exactly one final phase review/testing/report task covering coupled code, all LOG-01–07 checks, incorporation/current-owner consistency, complete regressions, packages and source/release readiness. One cohesive delivery milestone is intentional for this narrow feature; padding separate setup/clock/handler milestones would add no independent value. Earlier phases retain their scoped identities and exits; the seven LOG conditions extend the baseline acceptance set.

Phase exit requires the library/CLI logging contracts, complete regression/tooling and installed/source-rebuilt example evidence, verified task/milestone closures and code review. Version 0.5.0 follows the existing default-branch exact-source/tag/source-wheel-bundle/SHA256SUMS/hosted-readback release gate. Native execution limits remain explicit. See completed [feature evidence](features/006_c33ec54-progress-logging/reports/5.1.md) and the canonical [task list](TASKS.md).
