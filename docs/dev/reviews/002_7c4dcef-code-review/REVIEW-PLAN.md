# Code review plan

## Campaign and scope

- Campaign: `002_7c4dcef`; directory: `docs/dev/reviews/002_7c4dcef-code-review/`.
- Starting and reviewed code baseline: `7c4dcef1c171572e7868d3a03c959ea1c2f87b32`.
- Creation parent and eventual integration target: `main`; branch-off commit: `7c4dcef1c171572e7868d3a03c959ea1c2f87b32`; working branch: `revision/002_7c4dcef-code-review`.
- Request: "start a new code review campaign for the current codebase". Authorized now: allocate the campaign, prepare its review plan/report and entry HANDOFF, commit/publish/read back, then stop.
- Objective: assess correctness, contract conformance, resource/concurrency behavior, robustness, maintainability and test quality across the codebase.
- Included owners: `src/archive_line_index/`, `tests/`, `scripts/`, `pyproject.toml` and current public documentation.

## Review criteria

| Criterion | Required assessment |
| --- | --- |
| C-001 | Public API, validation, source types and error categories match accepted contracts; arguments fail before avoidable acquisition or mutation. |
| C-002 | Byte fidelity, LF/BOM rules, canonical Q/eight-byte offsets and EOF sentinel remain correct under chunk boundaries, overflow and allocation failure. |
| C-003 | Owned resources and workers have explicit transfer, cancellation and successful-close guarantees; borrowed resources remain borrowed and primary failures survive cleanup. |
| C-004 | Successful EOF/completed indexes require terminal validation; ordinary I/O and dependency failures preserve the specified category/cause without partial success. |
| C-005 | Every supported archive obeys sole-regular-member policy, signature precedence, no member-path extraction and truthful dependency/buffer limits. |
| C-006 | Persistence validates complete representations and protects destinations through the publication commit point; failure diagnostics match actual filesystem state. |
| C-007 | All CLI forms use the library once for equivalent paired outputs, naming/protection/status rules and accurate partial-publication ownership. |
| C-008 | Actual artifacts expose the supported API outside the checkout, rebuild from source, exclude credentials/development inputs as required and pass the independent complete inventory/naming/checksum gates. |

## Review order

| Unit | Scope | Dependencies | Criteria |
| --- | --- | --- | --- |
| U-001 | Public surface, source detection, offset model and scanner | None | C-001, C-002 |
| U-002 | Common stream, backend protocol and ownership | U-001 | C-001, C-003, C-004 |
| U-003 | ZIP and plain/gzip/bzip2/xz TAR adapters | U-001, U-002 | C-003, C-004, C-005 |
| U-004 | 7z adapter and bounded producer bridge | U-001, U-002 | C-003, C-004, C-005 |
| U-005 | SQLite/raw persistence and filesystem publication | U-001 | C-001, C-006 |
| U-006 | Facade, CLI and cross-format composition | U-001–U-005 | C-001, C-003, C-004, C-007 |
| U-007 | Packaging, release helpers, test quality and public guidance | U-001–U-006 | C-008 |

## Consolidation and stopping

After all selected units, consolidate canonical findings, counts, priorities, coupled risks, deferred checks and a proposed revision queue. Stop before repairs, integration, release or campaign closure unless separately authorized.
