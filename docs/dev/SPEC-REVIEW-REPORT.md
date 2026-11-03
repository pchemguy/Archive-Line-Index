# SPEC review report

## Current gate

State: **Ready for the SPEC acceptance checkpoint**, based on the complete corrected contract set and its conformance to accepted design. Human acceptance remains pending; PLAN authoring must wait for it and DOCS-005 completion/publication/issue closure. There are no unresolved confirmed document findings. This is document readiness, not implementation or dependency verification.

Review date: 2026-11-03. Review performed by the authoring agent through design/contract comparison, boundary analysis and document checks. The review was not an independent implementation audit.

## Reviewed identities

The following SHA-256 identities identify the corrected proposed scope exactly. This report covers all six contract documents as one set.

| Reviewed artifact | SHA-256 |
| --- | --- |
| [SPEC.md](SPEC.md) | `29d6d6dc469ddd61943c3c3d35227bfcdcd45c9abe01eadc7e9f2633da4df74b` |
| [spec/archive-handling.md](spec/archive-handling.md) | `53eae2d7bb9fe004d4b78987cf379a31062877f7b54c24c38ac9cba981f009df` |
| [spec/content-stream.md](spec/content-stream.md) | `d080bee124f4c49b86bad070d2edfa3d0ed77efee4ed1c2c00e53c36234bcefd` |
| [spec/line-index.md](spec/line-index.md) | `444c48b11d9645b2a1f4527cb6853c79a1542939f25830112d8c392480ec3735` |
| [spec/persistence.md](spec/persistence.md) | `e8aed8ee353d5f8ff4c07a779deb687012cc14d95a0eb44078d560d6881ec822` |
| [spec/public-api.md](spec/public-api.md) | `13d4b476f6a675427661f2857b2e41c778c58cff592f6f8ead3ef12bc3ea2332` |

The governing set is accepted in the history contained by `f2630445eafd76ead0b9be44e780c0274b25f873`; these source bytes were not changed during specification preparation.

| Governing artifact | SHA-256 |
| --- | --- |
| [PROJECT.md](PROJECT.md) | `b2c2e55722e5bd68aef98b0dd82ef1116d71826730edc2ad98a1f4a9fe482b85` |
| [ARCHITECTURE.md](ARCHITECTURE.md) | `08a65b86da46847a99bea949590c0b04f614f86acf52e9942e1c86762e773b67` |
| [DECOMPOSITION.md](DECOMPOSITION.md) | `bbbacb93ea0e07b28c95690322b89c1ebe07c07079a20709649adb2d384a9fda` |
| [decomposition/public-api.md](decomposition/public-api.md) | `bb9fa69aeb8c90594e574dd7a7966c31056a6b899bdcb890290182e91df832ef` |
| [decomposition/internal-api.md](decomposition/internal-api.md) | `be853e14b93d5129c59419eabe64e9b44291f1df76a6b9656891faf234b08a61` |

## Initial review

The initial review assessed intended outcomes and non-goals, provider/consumer interfaces, canonical data ownership, dependency direction, successful and failed completion, resource release, persistence commit points and objective integrated acceptance. It found two ambiguities requiring correction. Initial content identities for the affected artifacts were `26bc38d526a84441b872b44f040650a5785728670960956e5f3993b5a28bf8e0` (content stream) and `cc85b6faedd27bac7a5bb3e6faaf434c83c80b8f450159742095b33c2241be49` (persistence). Unchanged artifacts retain the identities above.

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

## Revision 1

The content-stream owner clarified argument rejection versus acquired-data failures and specified the internal reader/producer validation seams. The persistence owner required a self-contained SQLite database, checkpoint completion where applicable, closed handles and cleanup restricted to owned sidecars. The corrected states are the exact identities in the reviewed table.

Recheck: both findings are resolved. A rejected read argument leaves state/progress unchanged; subsequent valid reads remain eligible. Failure during delivery or finalization cannot become EOF. A SQLite destination cannot depend on temporary sidecars. Publication remains a separate commit point, so a subsequent temporary cleanup error accurately reports that a complete destination already exists.

Document checks verified local links, unique acceptance IDs, heading/list/code-block structure, unwrapped prose/list items, unchanged accepted design identities and pending DOCS-005 state. Review confirmed that the contracts do not add public entry points or reverse dependencies. No unresolved material contract/design choice blocks the SPEC checkpoint.

## Evidence limits

No application source exists yet. No product tests, runtime/type checks, dependency integration, distribution build, filesystem fault-injection campaign, resource measurement or native target execution was performed. Numeric policies and failure guarantees are specified requirements to implement and verify. Actual dependency constraints and valid distribution version metadata must be established with implementation/build evidence; the report does not claim that an installed dependency or package is already suitable. Whole-document-package QC remains a later preparation task.
