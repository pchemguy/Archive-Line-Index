# SPEC review report

## Current gate

State: **Ready for the amended design/SPEC acceptance checkpoint**, based on the CLI-expanded contract set and its consistency with the corresponding revised design. The human authorized the scope expansion and upstream edits; approval of the exact amended document set remains pending. PLAN authoring must wait for that approval and DOCS-005 completion/publication/issue closure. There are no unresolved confirmed document findings. This is document readiness, not implementation or dependency verification.

Review date: 2026-11-03. Review performed by the authoring agent through design/contract comparison, boundary analysis and document checks. The review was not an independent implementation audit.

## Reviewed identities

The following SHA-256 identities identify the corrected proposed scope exactly. This report covers all seven contract documents as one set, including the CLI contract.

| Reviewed artifact | SHA-256 |
| --- | --- |
| [SPEC.md](SPEC.md) | `70a815a5d4bce2a03e22c31caab6b5853ab441ffc323b9a49c0ed18a5c82dd68` |
| [spec/archive-handling.md](spec/archive-handling.md) | `53eae2d7bb9fe004d4b78987cf379a31062877f7b54c24c38ac9cba981f009df` |
| [spec/cli.md](spec/cli.md) | `5e3f07418eed73e365eacb27c581acc3dd51cab861f6661802977ed920a33a86` |
| [spec/content-stream.md](spec/content-stream.md) | `d080bee124f4c49b86bad070d2edfa3d0ed77efee4ed1c2c00e53c36234bcefd` |
| [spec/line-index.md](spec/line-index.md) | `444c48b11d9645b2a1f4527cb6853c79a1542939f25830112d8c392480ec3735` |
| [spec/persistence.md](spec/persistence.md) | `bb89f91105d4f1593c1ba2462559cf2004cb85a46f28a75d9a2fd8bddfe588bb` |
| [spec/public-api.md](spec/public-api.md) | `611e302b15dc7206ab2367e6bd0054874977fb03f408f8f28a5623a45f3b1303` |

The current governing set includes the human-authorized CLI scope amendment. The prior accepted design is contained by `f2630445eafd76ead0b9be44e780c0274b25f873`; original review identities from `88cbac38edf1db0970ff239b1b00d402f00b8c5e` are retained in the Revision 1 baseline below. Current revised design states require acceptance together with the amended SPEC.

| Governing artifact | SHA-256 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | `84c2fbe4bb54d38bcc3426dc6460bcd4bb0a045e812502a13a210a5acc5d056c` |
| [ARCHITECTURE.md](ARCHITECTURE.md) | `adf0fab5199e8676cd585ce8ed6652b821f6fcd4590f3a9125a2c5672e85a1db` |
| [DECOMPOSITION.md](DECOMPOSITION.md) | `a9df24ec01f2dc470f020f29ae45e89a6a5b36602aa9cb01ee470be624135af6` |
| [decomposition/public-api.md](decomposition/public-api.md) | `fac8ed1680f4adb2e6e7d251f2aee5e4fa316e2d78a8e6b6bd078da796b4bd44` |
| [decomposition/internal-api.md](decomposition/internal-api.md) | `ef90a5d76bc0456e3f926e439a8983d987c05d65e88df31cb70d3bc7223b16c6` |

## Initial review

The initial review assessed intended outcomes and non-goals, provider/consumer interfaces, canonical data ownership, dependency direction, successful and failed completion, resource release, persistence commit points and objective integrated acceptance. It found two ambiguities requiring correction. Initial content identities for the affected artifacts were `26bc38d526a84441b872b44f040650a5785728670960956e5f3993b5a28bf8e0` (content stream) and `cc85b6faedd27bac7a5bb3e6faaf434c83c80b8f450159742095b33c2241be49` (persistence). The initial reviewed scope is identified by the Revision 1 baseline below.

| Finding | Location and consequence | Owning correction and objective recheck | Disposition |
| --- | --- | --- | --- |
| SPEC-R001 | Content-stream state/failure paragraph did not distinguish invalid arguments from failures after data acquisition; implementations could close or poison a stream after a rejected argument. | Content-stream contract must explicitly preserve state/no backend progress for argument rejection, while delivery/limit/finalization/allocation failures retain FAILED and trigger cleanup. Recheck read-state precedence against the public design and zero-size rules. | Resolved in Revision 1. |
| SPEC-R002 | SQLite writer completion did not explicitly prohibit data remaining only in a temporary WAL/journal sidecar; publishing the main file alone could lose completed offsets. | Persistence contract must require a standalone validated database, completed checkpoint/closed handles if WAL is used, and ownership-aware sidecar cleanup. Recheck the publication sequence and primary/cleanup error separation. | Resolved in Revision 1. |

## Contract-to-design coverage

| Concern and acceptance groups | Design owners | Assessment |
| --- | --- | --- |
| Scope, independent use, platforms and distribution: SYS-01–02, SYS-10–12, API-01–05 | PROJECT, public facade and canonical public exports | All accepted capabilities/exclusions are represented; signatures/types are referenced from the public design rather than copied. Installed-artifact evidence is required without inventing external publication authority or unavailable-native gates. |
| Payload fidelity, reader/state/limit semantics: SYS-04–06, STR-01–06 | Content stream, backend reader and shared errors | Zero-size reads are separated from validated EOF; retained failure, ordinary argument rejection, declared/actual limits, cleanup priority and internal provider outcomes are defined. |
| Source detection, format validation and 7z lifecycle: SYS-01, SYS-04–06, ARC-01–06 | Detector, selector, adapters and producer bridge | Supported TAR filters and suffix precedence are explicit; unsupported/malformed/structural failures remain distinct. Cooperative cancellation has finite package waits but no invented hard dependency deadline. Queue limits and dependency-suitability evidence are specified. |
| LF/BOM offsets and numeric/storage bounds: SYS-03, SYS-06, IDX-01–06 | Scanner, ReadableBinary and canonical offset model | Concrete examples, local byte coordinates, short-read handling, borrowed ownership, overflow and representation validation are consistent with the accepted model. No text parsing or line accumulation is introduced. |
| Format equivalence, protection and publication: SYS-07–09, PER-01–07 | SQLite/raw adapters, offset model and publication helper | Exact representations, standalone SQLite completion, independent writes, exclusive creation, replacement, post-publication cleanup and corruption rejection have canonical behavioral owners. No writer locks or source identity are added. |
| CLI execution and naming: SYS-13, CLI-01–06 | CLI adapter and wrappers, index-building facade and SQLite/raw writers | One-target console/module/imported invocation shares a downward-only adapter and one completed offset array for both outputs. Input-directory/stem naming is confined to CLI, imports perform no work, return statuses do not exit in-process callers, and preflight/publication checks protect both destinations. Partial publication is reported without inventing a cross-file transaction. |

## Revision 1

The content-stream owner clarified argument rejection versus acquired-data failures and specified the internal reader/producer validation seams. The persistence owner required a self-contained SQLite database, checkpoint completion where applicable, closed handles and cleanup restricted to owned sidecars. The corrected initial states are the exact identities in the Revision 1 baseline below.

Recheck: both findings are resolved. A rejected read argument leaves state/progress unchanged; subsequent valid reads remain eligible. Failure during delivery or finalization cannot become EOF. A SQLite destination cannot depend on temporary sidecars. Publication remains a separate commit point, so a subsequent temporary cleanup error accurately reports that a complete destination already exists.

Document checks verified local links, unique acceptance IDs, heading/list/code-block structure, unwrapped prose/list items, unchanged accepted design identities and pending DOCS-005 state. Review confirmed that the contracts do not add public entry points or reverse dependencies. No unresolved material contract/design choice blocks the SPEC checkpoint.

### Revision 1 baseline

The following identities retain the initial corrected SPEC set and its governing accepted design as published in `88cbac38edf1db0970ff239b1b00d402f00b8c5e`. They establish historical review scope, not approval of the CLI amendment.

| Reviewed artifact | SHA-256 |
| --- | --- |
| [SPEC.md](SPEC.md) | `29d6d6dc469ddd61943c3c3d35227bfcdcd45c9abe01eadc7e9f2633da4df74b` |
| [spec/archive-handling.md](spec/archive-handling.md) | `53eae2d7bb9fe004d4b78987cf379a31062877f7b54c24c38ac9cba981f009df` |
| [spec/content-stream.md](spec/content-stream.md) | `d080bee124f4c49b86bad070d2edfa3d0ed77efee4ed1c2c00e53c36234bcefd` |
| [spec/line-index.md](spec/line-index.md) | `444c48b11d9645b2a1f4527cb6853c79a1542939f25830112d8c392480ec3735` |
| [spec/persistence.md](spec/persistence.md) | `e8aed8ee353d5f8ff4c07a779deb687012cc14d95a0eb44078d560d6881ec822` |
| [spec/public-api.md](spec/public-api.md) | `13d4b476f6a675427661f2857b2e41c778c58cff592f6f8ead3ef12bc3ea2332` |

| Governing artifact | SHA-256 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | `b2c2e55722e5bd68aef98b0dd82ef1116d71826730edc2ad98a1f4a9fe482b85` |
| [ARCHITECTURE.md](ARCHITECTURE.md) | `08a65b86da46847a99bea949590c0b04f614f86acf52e9942e1c86762e773b67` |
| [DECOMPOSITION.md](DECOMPOSITION.md) | `bbbacb93ea0e07b28c95690322b89c1ebe07c07079a20709649adb2d384a9fda` |
| [decomposition/public-api.md](decomposition/public-api.md) | `bb9fa69aeb8c90594e574dd7a7966c31056a6b899bdcb890290182e91df832ef` |
| [decomposition/internal-api.md](decomposition/internal-api.md) | `be853e14b93d5129c59419eabe64e9b44291f1df76a6b9656891faf234b08a61` |

## Evidence limits

No application source exists yet. No product tests, runtime/type checks, dependency integration, distribution build, filesystem fault-injection campaign, resource measurement or native target execution was performed. Numeric policies and failure guarantees are specified requirements to implement and verify. Actual dependency constraints and valid distribution version metadata must be established with implementation/build evidence; the report does not claim that an installed dependency or package is already suitable. Whole-document-package QC remains a later preparation task.

## Revision 2 — Minimal CLI scope

The human requested a minimal importable CLI for conveniently indexing one target and explicitly authorized changes to previously approved documents. The human then selected the input directory and input name without its extension as the default output location/stem, and required the raw-binary counterpart alongside SQLite. PROJECT, ARCHITECTURE, DECOMPOSITION and both API-design children express that scope directly; their exact amended states appear in the current governing table. The original design approval records remain historical evidence.

The proposal writes both SQLite (`.sqlite3`) and raw little-endian (`.u64`) outputs from one completed array, removes the final input suffix for the default stem, provides a shared `--output` stem and explicit `--overwrite`, and adds no batch mode, single-format selector or public library printing/exiting. Console execution and the guarded module runner use `archive_line_index.cli.main(argv)`. The CLI contract defines import-time behavior, argv validation, help/usage, expected errors/interruption, destination protection and post-publication failure reporting. These concrete surface choices are proposed for the human's acceptance; they are not attributed to the human's request beyond the specified single-target/importable/naming/two-format requirements.

Recheck covered every changed scope/exclusion statement, separate package-root versus CLI-submodule exports, downward dependencies, ownership of the completed array, default/explicit stems, both outputs and input aliases, existing destinations, second-writer failure, late writer cleanup errors and installed entry-point behavior. The library still receives explicit destination paths; CLI naming does not alter persistence semantics. SQLite is written first, followed by raw; a later failure retains and identifies any already published output. Both paths are preflighted before scanning, and only both successful writes yield the success summary. One integrated acceptance condition and six CLI conditions extend the set from 42 to 49 uniquely identified conditions. No unresolved confirmed finding remains in this amended scope.

The current reviewed identities cover SPEC and six children. Governing hashes match the revised design, local links resolve, Markdown prose/list items remain unwrapped and the unchanged core contract/model surfaces are retained. No production CLI implementation, entry-point metadata change or runtime test was performed; implementation and packaging remain future work. The amended upstream set and SPEC must be accepted before dependent PLAN authoring.
