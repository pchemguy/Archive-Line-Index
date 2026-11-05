# Comprehensive code and documentation review plan

## Campaign and authority

Campaign 009_2094900-code-docs; full reviewed/branch-off baseline 209490063eb2e299243fc7ad99e63a08305e0f3e; working branch revision/009_2094900-code-docs; creation parent and eventual return target main. The user authorized opening and running a comprehensive code/docs review. Scope is assessment, controlled local verification and published review records only; repairs, revision execution, closure, integration, version changes and release publication are not selected.

## Coverage and sequence

| Unit | Code/tests | Documentation and criteria | Evidence |
| --- | --- | --- | --- |
| U-001 | Public exports/entry wrapper, source normalization, API facade, errors, offsets, scanner, stream; their unit/integration coverage. | PROJECT/architecture/decomposition and public/stream/index/progress contracts; input validation, bounds, ownership, EOF, progress, docstrings and error guarantees. | Inspect complete owning modules, representative failure tests, targeted probes for suspected gaps. |
| U-002 | Format detector, all backend modules, producer/7z bridge; format/lifecycle/backpressure tests and helpers. | Archive/internal reader contracts and README backend guidance; validation before/after payload, size/CRC, cancellation, resource ownership and memory claims. | Inspect every backend module and consequential tests, probe concrete uncertain branches without production edits. |
| U-003 | Filesystem publication, raw/SQLite persistence, CLI; associated tests. | Persistence/API/CLI contracts and README workflows; schema/encoding, races, atomicity, partial publication, logging restoration/status and cross-platform assumptions. | Complete module review and realistic negative/outcome probes as needed. |
| U-004 | Packaging scripts, configuration, all remaining test/support modules and current maintained docs. | Build/distribution/release-name contracts, module docs, examples, current links/navigation, layout/test correspondence and overall consistency. | Full pytest/coverage, Ruff lint/format, strict mypy, native build/bundle/content/name checks and current-document link/inventory checks. |

[REVIEW-REPORT.md](REVIEW-REPORT.md) owns stable findings, no-finding coverage, observed execution and limitations. Commit/publish/read back the opening and each unit's report before the next unit or other project work. Evidence mode is repository inspection and controlled local execution, with no independent external research unless a concrete dependency question requires authoritative verification.

## Boundaries and stopping

Inventory all project-owned production/script/test modules and current root/development docs; review supplied SDD plugin code as externally maintained tooling, not project implementation. Exclude closed campaign/feature/phase reports, prior preparation/QC reports and manual AI transcripts from current-validity review. Discover protected paths by names only; retain them unchanged. Report unclear or unavailable behavior as such, not as proven defects. Linux is available; native Windows/macOS/other Python/big-endian, remote CI and hosted release-byte verification are not established by local checks. No publication/settings changes other than the authorized review branch records.

Every finding records location, evidence, consequence, priority, confidence, proposed bounded correction and an objective recheck. Passing tests do not substitute for code review or prove absent defects. Finish with coverage, actual checks, findings and proposed priorities; stop before repairs or integration and leave the campaign Open.
