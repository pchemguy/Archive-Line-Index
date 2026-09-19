# Project layout

## 1. Purpose and authority

This document is the compact authoritative entry point for the Archive Line
Index project's physical organization. The complete LAYOUT tree defines where
production code, tests, development specifications, plans, and generated
artifacts belong; the responsibility of each important location; and the
import boundaries that preserve the system architecture.

The root specification defines required system behavior. The root plan defines
the ordered implementation strategy. The LAYOUT tree owns neither behavior nor
implementation sequencing: it maps those concerns onto files and directories.
When a proposed implementation does not fit this layout cleanly, the
architectural boundary and the applicable LAYOUT nodes shall be reconsidered
rather than working around the mismatch with circular imports or duplicated
logic.

## 2. Repository overview

```text
archive-line-index/
├── repository-root files
├── docs/
│   └── dev/
│       ├── SPEC.md and spec/
│       ├── PLAN.md and plan/
│       ├── layout.md
│       └── layout/
├── src/
│   └── archive_line_index/
└── tests/
    ├── helpers/ and fixtures/
    ├── unit/
    └── integration/
```

The complete intended repository tree and root-file ownership are defined in
[layout/repository.md](layout/repository.md). The documentation, production,
test, and artifact subtrees are owned by the focused children listed below.

## 3. LAYOUT decomposition

| LAYOUT node | Canonical physical responsibility |
| --- | --- |
| This root | Authority, high-level repository map, child scopes, cross-tree routing, global invariants, and change rules |
| [layout/repository.md](layout/repository.md) | Complete repository tree, repository-root files, package naming, `src`-layout convention, and repository-wide tool configuration |
| [layout/docs.md](layout/docs.md) | Documentation directories and the ownership boundaries within the SPEC, PLAN, and LAYOUT trees |
| [layout/src.md](layout/src.md) | Production package, archive backends, persistence package, module ownership, and normative import directions |
| [layout/tests.md](layout/tests.md) | Test directories, fixtures, helpers, unit/integration organization, and production-to-test mapping |
| [layout/packaging-runtime.md](layout/packaging-runtime.md) | Generated and runtime artifacts, distribution contents, installed behavior, and CLI absence |

These boundaries follow physical ownership rather than mirroring SPEC
components or PLAN phases. For an ordinary change, load this root and the one
focused child that owns the affected location. Load another child only when the
change crosses a physical boundary.

## 4. Cross-tree routing

| Architectural area | SPEC owner | Physical implementation owner | Test owner | Principal PLAN phase or phases |
| --- | --- | --- | --- | --- |
| Public API and composition | [spec/public-api.md](spec/public-api.md) | `src/archive_line_index/__init__.py`, `api.py`, and `errors.py`; see [layout/src.md](layout/src.md) | Public-path integration tests and focused module tests; see [layout/tests.md](layout/tests.md) | [plan/plain-stream-index-mvp.md](plan/plain-stream-index-mvp.md), [plan/archive-streams.md](plan/archive-streams.md), [plan/index-persistence.md](plan/index-persistence.md), and [plan/package-integration.md](plan/package-integration.md) |
| Sequential content stream | [spec/content-stream.md](spec/content-stream.md) | `sources.py`, `stream.py`, and the backend protocol; see [layout/src.md](layout/src.md) | Stream/source unit tests and content-stream/resource integration tests; see [layout/tests.md](layout/tests.md) | [plan/plain-stream-index-mvp.md](plan/plain-stream-index-mvp.md) and [plan/archive-streams.md](plan/archive-streams.md) |
| Archive handling | [spec/archive-handling.md](spec/archive-handling.md) | `formats.py` and `backends/`; see [layout/src.md](layout/src.md) | Format/backend unit tests and cross-format integration tests; see [layout/tests.md](layout/tests.md) | [plan/archive-streams.md](plan/archive-streams.md) |
| Line indexing | [spec/line-index.md](spec/line-index.md) | `offsets.py` and `scanner.py`; see [layout/src.md](layout/src.md) | Offset/scanner unit tests and index-building integration tests; see [layout/tests.md](layout/tests.md) | [plan/plain-stream-index-mvp.md](plan/plain-stream-index-mvp.md) |
| Index persistence | [spec/persistence.md](spec/persistence.md) | `persistence/`; see [layout/src.md](layout/src.md) | Persistence unit tests and persistence-equivalence integration tests; see [layout/tests.md](layout/tests.md) | [plan/index-persistence.md](plan/index-persistence.md) |
| Packaging and installed use | System-wide acceptance conditions in [SPEC.md](SPEC.md) | `pyproject.toml`, distribution contents, and installed package; see [layout/repository.md](layout/repository.md) and [layout/packaging-runtime.md](layout/packaging-runtime.md) | Installed-wheel and representative workflow verification | [plan/package-integration.md](plan/package-integration.md) |

Behavioral guarantees remain canonical in the SPEC tree, construction order in
the PLAN tree, and detailed file ownership in the LAYOUT tree. This table is a
routing aid and does not replace those definitions.

## 5. Global physical invariants

1. Production code lives only under `src/archive_line_index/`; tests and
   development documents are not runtime modules.
2. The `src` layout is real: tests and installed-use checks exercise an
   installed package or an equivalent editable installation and do not rely on
   the repository root appearing on `sys.path`.
3. Internal modules import definitions from their canonical owning modules,
   never from the package-level re-export surface.
4. Production imports obey the acyclic dependency directions defined in
   [layout/src.md](layout/src.md). Reciprocal imports are prohibited.
5. `py7zr` remains localized to the 7z backend; importing standard-library
   backends does not eagerly import 7z implementation state.
6. The test tree mirrors production ownership without becoming a Python
   package or containing production algorithms.
7. Generated archives, indexes, temporary persistence files, build products,
   and test caches are not source content and are not committed.
8. Archive backends stream member bytes and never create a decompressed member
   file, including as a temporary artifact.
9. Public distribution and import names remain `archive-line-index` and
   `archive_line_index`, respectively.
10. Metadata, archive identity, automatic source/index association, mmap
    access, and a CLI remain absent unless SPEC, PLAN, LAYOUT, implementation,
    and tests are revised coherently.

## 6. Change and refactoring rules

Layout changes follow the project's specification-driven development protocol:

1. Inventory the affected normative LAYOUT content and assign every item one
   canonical destination before moving it.
2. Reflect a component split or merge in the relevant SPEC ownership
   boundaries before remapping its physical implementation here.
3. Update this root when child scopes, cross-tree routing, global invariants, or
   the high-level repository map change.
4. Update the lowest applicable LAYOUT child with detailed file ownership and
   import constraints; reference its canonical definition rather than
   duplicating it in another node.
5. Update the PLAN with dependency-ordered tasks that leave every intermediate
   state testable.
6. Move production and test ownership together, update affected links, and
   remove obsolete paths and duplicate ownership descriptions.
7. Verify that this root still routes an ordinary task to a small focused set
   of child documents.

New general-purpose modules such as `utils.py`, `common.py`, or `helpers.py`
are prohibited unless they acquire a precise canonical responsibility that
cannot belong to an existing component. Cross-cutting constants and types live
with the component that owns their meaning, not in a convenience dumping
ground.

The current implementation layout is intentionally flat within cohesive
components. If archive handling, persistence, tests, packaging/runtime, or a
development-document node grows beyond a focused file, decompose its owning
LAYOUT child recursively. The original child becomes the overview for its new
subtree and continues to define child scopes, relationships, and applicable
invariants.

Do not split the LAYOUT tree according to PLAN phases or mechanically mirror
the SPEC tree. Refactor LAYOUT boundaries when physical ownership changes or
when routine work repeatedly requires unrelated layout context.
