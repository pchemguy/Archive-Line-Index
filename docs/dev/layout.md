# Project layout

## 1. Purpose and authority

This is the compact root of the Archive Line Index LAYOUT tree. The tree is the canonical map of physical project organization: locations, ownership boundaries, import constraints, tests, and artifacts. SPEC owns behavior and contracts; PLAN owns construction order; ROADMAP projects durable PLAN progress; LAYOUT maps these views onto the repository.

If an implementation does not fit cleanly, reconsider the architecture and LAYOUT rather than introduce circular imports or duplicate logic.

## 2. Repository overview

```text
archive-line-index/
├── repository-root files
├── docs/dev/{SPEC.md,spec/,PLAN.md,plan/,ROADMAP.md,layout.md,layout/}
├── src/archive_line_index/
└── tests/{helpers/,fixtures/,unit/,integration/}
```

The complete tree is defined in [layout/repository.md](layout/repository.md).

## 3. LAYOUT decomposition

| Node                                                | Canonical responsibility                                                                   |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| This root                                           | Authority, high-level map, routing, global invariants, and change rules                    |
| [repository.md](layout/repository.md)               | Complete tree, root files, package naming, `src` layout, and repository-wide configuration |
| [docs.md](layout/docs.md)                           | Documentation locations and SPEC/PLAN/LAYOUT ownership                                     |
| [src.md](layout/src.md)                             | Production packages, modules, backends, persistence, and imports                           |
| [tests.md](layout/tests.md)                         | Test locations, infrastructure, fixtures, and production-to-test mapping                   |
| [packaging-runtime.md](layout/packaging-runtime.md) | Runtime/generated artifacts, distributions, installed behavior, and CLI absence            |

For an ordinary change, load this root and the child owning the affected location. These boundaries follow physical ownership; they do not mirror SPEC components or PLAN phases.

## 4. Cross-tree routing

| Area            | SPEC                                                         | LAYOUT                                                                               | Tests                                   | PLAN                                    |
| --------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------ | --------------------------------------- | --------------------------------------- |
| API/composition | [public-api](spec/public-api.md)                             | [source](layout/src.md)                                                              | [unit/integration](layout/tests.md)     | MVP, archives, persistence, integration |
| Content stream  | [content-stream](spec/content-stream.md)                     | [source](layout/src.md)                                                              | [stream/resource](layout/tests.md)      | MVP, archives                           |
| Archives        | [archive-handling](spec/archive-handling.md)                 | [source](layout/src.md)                                                              | [backend/cross-format](layout/tests.md) | archives                                |
| Line index      | [line-index](spec/line-index.md)                             | [source](layout/src.md)                                                              | [scanner/index](layout/tests.md)        | MVP                                     |
| Persistence     | [persistence](spec/persistence.md)                           | [source](layout/src.md)                                                              | [persistence](layout/tests.md)          | persistence                             |
| Packaging       | [system acceptance](SPEC.md#11-system-acceptance-conditions) | [repository](layout/repository.md), [packaging/runtime](layout/packaging-runtime.md) | installed workflows                     | integration                             |

PLAN phase links and order are canonical in [PLAN.md](PLAN.md). This table is only a routing map; detailed behavior, sequencing, and physical ownership stay in their respective trees.

[ROADMAP.md](ROADMAP.md) is the PLAN-derived durable progress view. It owns no behavior, implementation order, or physical-layout requirement.

## 5. Global physical invariants

1. Runtime code lives only under `src/archive_line_index/`; tests and development documents are not runtime modules.
2. Tests exercise an installed package or equivalent editable installation; they do not inject the repository root into `sys.path`.
3. Internal modules import from canonical owners, not package re-exports, and obey the acyclic directions in [layout/src.md](layout/src.md).
4. Only the 7z backend imports `py7zr`.
5. Generated inputs, indexes, temporary files, build output, and caches are not source content. Backends never extract a decompressed member file.
6. Distribution/import names remain `archive-line-index` and `archive_line_index`. A CLI and other current non-goals require coordinated SPEC, PLAN, LAYOUT, implementation, and test changes.

## 6. Change and refactoring rules

1. Assign every affected ownership statement to one canonical LAYOUT node before moving it.
2. Reflect component boundary changes in SPEC, then update the owning LAYOUT node and dependency-ordered PLAN tasks.
3. Update this root only when its map, child scopes, routing, invariants, or tree-wide rules change.
4. Move production and test ownership together; update links and remove stale paths and normative duplication.
5. Verify that routine work still needs only this root and a small focused set of children.

Do not add dumping-ground modules such as `utils.py`, `common.py`, or `helpers.py`; a new module needs a precise canonical responsibility. Decompose an oversized LAYOUT child recursively by physical ownership, leaving the child as its subtree overview. Never split LAYOUT by PLAN phase or mechanically copy the SPEC tree.
