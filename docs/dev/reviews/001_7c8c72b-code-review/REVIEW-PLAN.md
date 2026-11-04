# Code review plan

## Campaign and scope

- Campaign: `001_7c8c72b`; directory: `docs/dev/reviews/001_7c8c72b-code-review/`.
- Starting and reviewed code baseline: `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`; source is published main after completed v0.4.0 delivery. Release tag remains at `7ee4afc200c7fded93880397128b0a9e217f3c52`.
- Creation parent and eventual integration target: `main`; branch-off commit: `7c8c72b0791be95f3b28bbf193bbc29f8432d0c2`; working branch: `revision/001_7c8c72b-code-review`; publication destination: origin at the established Archive-Line-Index repository.
- Request: “Open code review campaign.” Authorized now: allocate the campaign, prepare its review plan/report and entry HANDOFF, commit/publish/read back, then stop. Review execution, source repairs, integration and another release are not selected by this opening request.
- Objective: assess correctness, contract conformance, resource/concurrency behavior, robustness, maintainability and test quality across the delivered implementation and its consequential handoffs.
- Included owners: `src/archive_line_index/`, `tests/`, `scripts/`, `pyproject.toml` and current public documentation. Accepted PROJECT/ARCHITECTURE/DECOMPOSITION/SPEC/PLAN/layout and focused children supply criteria; TASKS and completed release evidence supply provenance rather than proof of fresh review.
- Exclusions: installed plugin internals, unrelated/manual-provenance branches, closed historical campaign/phase records as routine review targets, new features, external publication effects and unavailable target-native execution. Preserve existing releases and completed task/tracking state.
- Companion report: [REVIEW-REPORT.md](REVIEW-REPORT.md).
- State: Open; planned review units have not been executed.

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

| Unit | Scope | Dependencies | Criteria | Scenarios and evidence method |
| --- | --- | --- | --- | --- |
| U-001 | Public surface, source detection, offset model and scanner | None | C-001, C-002 | Inspect exports, option checks and source classification; exact LF/BOM/EOF arrays, short reads, range/allocation failures, long-line boundedness and signature/suffix conflicts. |
| U-002 | Common stream, backend protocol and ownership | U-001 | C-001, C-003, C-004 | Check zero/bounded/unbounded/readinto operations, byte capacity, inclusive limits, retained failure/closed precedence, constructor failures, cleanup notes and retry. |
| U-003 | ZIP and plain/gzip/bzip2/xz TAR adapters | U-001, U-002 | C-003, C-004, C-005 | Inspect sole-member selection and no filesystem extraction; actual empty/nested/special/extra/late members, truncation, CRC/trailers, unavailable codecs and ordinary source errors. |
| U-004 | 7z adapter and bounded producer bridge | U-001, U-002 | C-003, C-004, C-005 | Inspect actual py7zr callback integration, metadata and thread ownership; progressive delivery, finite queue/block storage, cancellation under backpressure, startup/terminal failures, cleanup retry and interruption. |
| U-005 | SQLite/raw persistence and filesystem publication | U-001 | C-001, C-006 | Check canonical schema/little-endian bytes, read-only loading, malformed inputs, native-endian conversion, exclusive/overwrite publication races and pre/post-publication failure ownership. |
| U-006 | Facade, CLI and cross-format composition | U-001–U-005 | C-001, C-003, C-004, C-007 | Trace one scan/shared array through SQLite then raw; default/explicit stems, aliases, overwrite, statuses/import effects, late archive failures and accurate partial-publication diagnostics. |
| U-007 | Packaging, release helpers, test quality and public guidance | U-001–U-006 | C-008 and cross-unit regression | Review metadata/entry points, dependency constraint, installed native/source-rebuilt consumers, safe inventory and stable bundle/name/checksum gates. Assess tests for independent expectations and missing negative coverage; verify README claims/examples against code, then consolidate findings. |

## Evidence and persistence

On a subsequent review instruction, inspect source before interpreting passing tests. Record exact file/line evidence, consequences, confidence, concrete negative scenarios and objective rechecks. Distinguish defects from recommendations and evidence gaps; allocate stable R-001 onward only for supported findings. Missing coverage alone does not prove a runtime defect. Record no-finding coverage explicitly.

Use focused pytest reproductions where useful and run Ruff/strict mypy or installed/build checks when they answer the selected concern. Preserve independent expected values; assess mocks against actual dependency and filesystem behavior. Prior 687-test/95% results are historical baseline evidence, not execution in this campaign. Linux/bash and the existing Python 3.12 runtime are available; use --no-native-parser for the previously observed mypy container issue if necessary. Native Windows/macOS/Python 3.11/big-endian checks require suitable facilities; report unavailable execution without inventing a result or blocking independent review.

Update and commit the report after each review unit, then push/read back that checkpoint before the next unit. Keep reviewed code pinned to the baseline; if source changes, record the new exact candidate and reassess affected coverage. No source/test/packaging/governing-document repair is authorized merely by finding a problem. Review records and scratch reproductions may be used within an actual review request without changing the reviewed implementation.

## Consolidation and stopping

After all selected units, consolidate canonical findings, counts, priorities, coupled risks, deferred checks and a proposed revision queue. Stop before repairs, integration, release or campaign closure unless separately authorized. This opening checkpoint stops before U-001. Campaign records remain on the revision branch; main and the v0.4.0 tag remain unchanged.
