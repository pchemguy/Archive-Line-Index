# Packaging, installation, and runtime artifacts

## 1. Scope

This node owns generated and runtime artifacts, build output, distribution
contents, installed-package behavior, and the physical implications of the
current absence of a command-line interface.

## 2. Generated and runtime artifacts

Index outputs are runtime artifacts, not repository content. Callers may place
them next to the source archive, but the package does not infer, prescribe, or
persist their association with that archive.

The relevant artifact classes are:

| Artifact | Ownership | Repository status |
| --- | --- | --- |
| SQLite database containing `line_index` | Caller-selected destination | Ignored |
| Raw little-endian `uint64` offset file | Caller-selected destination | Ignored |
| Temporary raw output | Raw persistence adapter until publication | Ignored and cleaned on failure |
| Temporary SQLite index database | SQLite persistence adapter until publication | Ignored and cleaned on failure |
| Temporary SQLite journal/WAL files | SQLite during persistence | Ignored |
| Generated test archives and indexes | Individual test via `tmp_path` | Never committed |
| `build/`, `dist/`, and wheel metadata | Packaging tools | Ignored |
| `.pytest_cache/`, coverage data, HTML coverage | Test tools | Ignored |

The raw-file extension and database filename are not architectural identifiers.
Examples such as `.u64` or `.sqlite3` may be used in documentation, but public
operations accept explicit destinations unless a later specification adds a
naming policy.

No decompressed member file is a normal project artifact. Archive backends must
stream member bytes and must not create extraction output, even temporarily.

## 3. Packaging and installed behavior

Only `src/archive_line_index/` is included as importable production code. Tests
and development documents are not imported at runtime. Any documentation or
license files included in source or wheel distributions are selected explicitly
through packaging configuration rather than by making them package modules.

The installed package must behave identically when invoked outside the
repository. Verification therefore includes building a wheel, installing it in
an isolated environment, importing the documented public surface, and running
representative plain and archive workflows without relying on repository-local
paths.

There is no command-line entry point or `__main__.py` in the current layout.
Adding a CLI is a feature and requires corresponding SPEC, PLAN, LAYOUT, and
test updates rather than an unplanned wrapper module.
