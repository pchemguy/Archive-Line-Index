# Repository organization

## 1. Scope

This node owns the complete repository tree, root files, and repository-wide physical conventions. Sibling nodes own documentation, source, tests, and packaging/runtime detail.

## 2. Complete repository layout

```text
archive-line-index/
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── docs/
│   └── dev/
│       ├── SPEC.md
│       ├── spec/
│       │   ├── public-api.md
│       │   ├── content-stream.md
│       │   ├── archive-handling.md
│       │   ├── line-index.md
│       │   └── persistence.md
│       ├── PLAN.md
│       ├── plan/
│       │   ├── plain-stream-index-mvp.md
│       │   ├── archive-streams.md
│       │   ├── index-persistence.md
│       │   └── package-integration.md
│       ├── ROADMAP.md
│       ├── layout.md
│       └── layout/
│           ├── repository.md
│           ├── docs.md
│           ├── src.md
│           ├── tests.md
│           └── packaging-runtime.md
├── src/
│   └── archive_line_index/
│       ├── __init__.py
│       ├── api.py
│       ├── errors.py
│       ├── sources.py
│       ├── formats.py
│       ├── stream.py
│       ├── offsets.py
│       ├── scanner.py
│       ├── backends/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── plain.py
│       │   ├── zip.py
│       │   ├── tar.py
│       │   └── sevenzip.py
│       └── persistence/
│           ├── __init__.py
│           ├── sqlite.py
│           └── raw.py
└── tests/
    ├── conftest.py
    ├── helpers/
    │   ├── archive_factory.py
    │   ├── binary_cases.py
    │   └── streams.py
    ├── fixtures/
    │   └── README.md
    ├── unit/
    │   ├── test_package.py
    │   ├── test_errors.py
    │   ├── test_sources.py
    │   ├── test_formats.py
    │   ├── test_stream.py
    │   ├── test_offsets.py
    │   ├── test_scanner.py
    │   ├── backends/
    │   │   ├── test_registry.py
    │   │   ├── test_plain.py
    │   │   ├── test_zip.py
    │   │   ├── test_tar.py
    │   │   └── test_sevenzip.py
    │   └── persistence/
    │       ├── test_sqlite.py
    │       └── test_raw.py
    └── integration/
        ├── test_content_stream.py
        ├── test_index_building.py
        ├── test_persistence_equivalence.py
        └── test_resource_lifecycle.py
```

The SPEC, PLAN, and LAYOUT trees may be decomposed further when a node becomes too broad, but new files must correspond to a meaningful architectural, implementation, or physical-ownership boundary. Production modules follow the same rule: a module is split only when it acquires multiple independently understandable responsibilities.

## 3. Repository-root files

### `pyproject.toml`

Owns build-system configuration, distribution metadata, the minimum supported Python version, runtime and development dependencies, package discovery, and tool configuration.

The distribution name is hyphenated for packaging, while the import package uses underscores:

```text
distribution: archive-line-index
import:       archive_line_index
```

The project uses a `src` layout. Test execution must therefore exercise the installed package or an equivalent editable installation rather than relying on the repository root accidentally appearing on `sys.path`.

`py7zr` is the only required third-party runtime dependency unless the specification is deliberately expanded. ZIP, TAR, SQLite, binary arrays, threading, queues, and codecs used for fixed binary serialization come from the Python standard library.

Tool settings that apply to the entire repository belong here when supported by the tool, including pytest discovery and optional coverage, formatting, or static-analysis configuration. Tool-specific standalone files should be added only when `pyproject.toml` cannot express the required configuration clearly.

### `README.md`

Provides the user-facing package overview, installation instructions, short examples, supported input formats, and links into the detailed development documentation. It does not duplicate the normative behavioral detail in the SPEC tree.

### `LICENSE`

Contains the project license and has no runtime role.

### `.gitignore`

Excludes build output, virtual environments, test caches, coverage output, editor state, generated archives, temporary persistence files, and local index databases or raw offset files. It must not ignore source fixtures intentionally kept under `tests/fixtures/`.
