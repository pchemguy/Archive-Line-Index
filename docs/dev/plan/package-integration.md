# Package integration plan

## 1. Capability delivered

This phase turns the fully implemented components into a release-ready package. It finalizes exports, packaging metadata, dependency bounds, user documentation, installed-package verification, slow resource tests, and complete acceptance coverage.

It introduces no new runtime capability. Any newly discovered behavioral gap is returned to the phase and SPEC node that owns it rather than implemented as integration-layer special handling.

## 2. Specifications implemented

This phase completes project-wide requirements from:

- [../SPEC.md](../SPEC.md);
- [../spec/public-api.md](../spec/public-api.md);
- [../spec/content-stream.md](../spec/content-stream.md);
- [../spec/archive-handling.md](../spec/archive-handling.md);
- [../spec/line-index.md](../spec/line-index.md);
- [../spec/persistence.md](../spec/persistence.md);
- [../layout.md](../layout.md).

## 3. Prerequisites

- Plain stream/index MVP, archive streams, and persistence phases are complete.
- All unit and integration tests from those phases pass.
- Public behavior and internal dependency directions are stable.

## 4. Ordered implementation tasks

### Task: finalize package exports

Review `src/archive_line_index/__init__.py` against `spec/public-api.md`. Export exactly the supported aliases, constants, class, functions, and exception hierarchy.

Add an installed/import-surface test that:

- imports every documented name from `archive_line_index`;
- checks no backend class, detector state, queue message, or persistence helper is accidentally exported;
- imports package submodules without circular-import failures;
- confirms internal modules do not import through package `__init__.py`.

Run import-surface tests plus the full unit suite.

### Task: finalize dependency and build metadata

Update `pyproject.toml` with complete distribution metadata, Python classifiers, platform-independent wheel settings, package discovery, license/readme inclusion, test extras, and the tested lower/upper `py7zr` bounds.

Verify the chosen dependency range by running the archive suite against the oldest and newest supported versions in isolated environments where practical. If compatibility differs, narrow the range rather than adding undocumented version branches.

Build source and wheel artifacts, inspect their contents, and install each into a clean environment outside the repository.

### Task: write the user README

Create or complete `README.md` using the stable public API.

Include:

- purpose and supported formats;
- installation;
- standalone `ContentStream` example;
- in-memory index example and EOF-sentinel explanation;
- SQLite and raw persistence examples;
- source ownership and successful-EOF integrity caveats;
- decompressed-offset/random-seek limitation;
- metadata/identity, mmap, encryption, and CLI non-goals;
- links to `docs/dev/SPEC.md`, `PLAN.md`, and `layout.md`.

Run every code example as a documentation test or equivalent executable smoke test against the installed wheel.

### Task: complete large-input and backpressure verification

Add slow/integration tests or test markers for:

- a generated decompressed payload substantially larger than ordinary buffers;
- a line much larger than the scan buffer;
- millions of short lines where feasible, validating approximately eight offset bytes per line plus overhead;
- a highly compressible archive whose expanded content is much larger than the archive;
- a deliberately slow 7z consumer demonstrating one-block lookahead;
- early cancellation under producer pressure;
- size-limit rejection before unbounded growth.

Measure process memory with a robust platform-appropriate technique where available. Keep a deterministic structural backpressure test in the normal suite even if memory measurement is marked slow.

Run slow tests separately, then the normal full suite.

### Task: complete cross-platform filesystem verification

Exercise path, temporary-sibling, atomic replacement, open-file, and cleanup behavior on Windows, Linux, and macOS environments available to the project.

Pay particular attention to:

- Windows replacement failure when a destination is open;
- path-like objects and Unicode paths;
- permission-denied behavior;
- cleanup after failed replacement;
- SQLite journal/WAL cleanup;
- caller-open stream lifetime;
- no reliance on POSIX-only rename, unlink, or descriptor semantics.

Keep platform-specific assertions conditional only when the operating-system contract genuinely differs; do not skip portable behavior.

### Task: run installed-package end-to-end workflows

In a clean environment outside the checkout:

1. install the built wheel;
2. generate one payload and equivalent ZIP, TAR, and 7z archives;
3. consume each through bounded `ContentStream` reads;
4. build and compare indexes;
5. persist one index to SQLite and raw formats;
6. reload and compare both;
7. repeat an early-close workflow;
8. verify no repository-local import or fixture path is required.

Record commands in project development instructions only if they are durable and generally useful; do not add generated artifacts to the repository.

### Task: reconcile documentation and acceptance coverage

Review the complete implementation against every normative section and acceptance condition in the SPEC tree.

For each condition, identify its automated test or explicit manual verification. Resolve omissions in the owning module/test/document rather than adding a central catch-all test.

Remove `docs/architecture.md` once all unique settled content has been integrated into `docs/dev/SPEC.md`, its subspecifications, and `layout.md`. Do not retain it as a second normative architecture description.

Run link/path checks across `docs/dev/`, README example tests, the complete pytest suite, and configured quality checks.

## 5. Final verification campaign

Run, in order:

1. focused unit tests for all production modules;
2. all integration tests;
3. repeated resource-lifecycle and 7z concurrency tests;
4. slow memory/backpressure tests;
5. formatting and static analysis;
6. source and wheel builds;
7. artifact-content inspection;
8. clean-environment source-distribution installation;
9. clean-environment wheel installation;
10. installed-package end-to-end workflows;
11. README example execution;
12. documentation link and ownership review.

Any failure returns work to the smallest owning task or phase. Re-run its focused tests, all dependent tests, and then resume this ordered final campaign.

## 6. Completion conditions

The project is complete when:

- every specified public name and only those names are exported;
- declared dependency bounds are tested and sufficient;
- all normal and slow tests pass on supported environments available to the project;
- built artifacts install and work outside the repository;
- README examples execute successfully;
- runtime memory and backpressure match the architecture;
- generated outputs and development-only files are absent from distributions;
- every SPEC acceptance condition has evidence;
- SPEC, PLAN, layout, README, and code describe one coherent current system;
- no obsolete exploratory architecture document remains necessary to understand or rebuild the project.
