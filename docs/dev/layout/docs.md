# Development-document organization

## 1. Scope

This node owns locations and document responsibilities under `docs/`; it does not redefine SPEC behavior, PLAN sequencing, or global LAYOUT rules.

## 2. SPEC tree

### `docs/dev/SPEC.md`

The compact authoritative entry point for the complete system specification. It owns project purpose, complete scope, non-goals, architectural decomposition, system-wide terminology and invariants, the subspecification scope map, and system-level acceptance conditions.

### `docs/dev/spec/public-api.md`

Owns the public Python surface:

- exported functions, classes, aliases, and constants;
- argument validation visible to callers;
- source ownership rules;
- context-management and closure contracts;
- exception hierarchy and propagation guarantees;
- which names are re-exported from `archive_line_index`.

It links to component specifications for detailed stream, archive, indexing, and persistence behavior rather than repeating those requirements.

### `docs/dev/spec/content-stream.md`

Owns the common sequential binary-stream contract, including read behavior, buffering guarantees, byte counting, decompressed-size limits, early closure, terminal integrity semantics, and the distinction between owned and caller-owned resources.

### `docs/dev/spec/archive-handling.md`

Owns input-format detection, recognized suffix behavior, exactly-one-member validation, special-entry rejection, encryption policy, backend-specific constraints, and 7z push-to-pull adaptation.

### `docs/dev/spec/line-index.md`

Owns LF byte-line semantics, initial UTF-8 BOM treatment, decompressed-offset meaning, the `array("Q")` representation, the EOF-sentinel invariant, the bounded-block scanning algorithm, and index completion rules.

### `docs/dev/spec/persistence.md`

Owns the SQLite table contract, raw little-endian `uint64` format, conversion between native-endian memory and portable persistence, transactional or atomic publication requirements for each representation, and persistence failure behavior.

It explicitly does not own source identity, index metadata, stale-index detection, or association of an index with an archive.

## 3. PLAN tree

### `docs/dev/PLAN.md`

The compact authoritative entry point for implementing the complete system from scratch. It declares the top-level phase order, phase dependencies, SPEC-to-plan mapping, and project-wide verification and completion rules.

### `docs/dev/plan/plain-stream-index-mvp.md`

Describes the smallest useful testable product: plain-source ownership and streaming, byte-line scanning, the in-memory offset representation, and a thin public composition path. It excludes archive decoding and persistence.

### `docs/dev/plan/archive-streams.md`

Adds content detection and the ZIP, TAR, and 7z backends to the already tested stream/index pipeline. It orders the pull-based backends before the threaded 7z adapter and includes cross-format behavioral verification.

### `docs/dev/plan/index-persistence.md`

Adds SQLite and raw-binary serialization from the stable in-memory offset contract. It includes failure-path tests and equivalence verification between the two representations.

### `docs/dev/plan/package-integration.md`

Completes the curated package exports, packaging verification, installed-package tests, documentation synchronization, and full acceptance suite. It must not become a catch-all for functionality that belongs in an earlier component phase.

## 4. LAYOUT tree

`docs/dev/layout.md` is the compact entry point; its `layout/` children own repository, documentation, source, tests, and packaging/runtime organization. Their precise scopes are canonical in that root.

SPEC nodes may refer to implementation locations, and PLAN tasks may name files to create or modify, but neither tree should duplicate the detailed ownership map in this LAYOUT tree.

## 5. Other documents under `docs/`

Exploration notes or temporary architecture documents outside `docs/dev/` are not normative. Once their settled content has been integrated into the authoritative SPEC, PLAN, and LAYOUT trees, they should be removed unless they retain a distinct, durable explanatory purpose.

New shared development documents shall be introduced only for a clear canonical responsibility not naturally owned by SPEC, PLAN, or LAYOUT. They must not become miscellaneous overflow containers.
