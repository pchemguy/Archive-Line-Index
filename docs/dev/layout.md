# Repository layout and ownership

## Scope

This document assigns physical homes to the components in [DECOMPOSITION](DECOMPOSITION.md) and the delivery boundaries in [PLAN](PLAN.md). It owns placement, not API behavior, implementation order or completion status. Listed production/test/build-helper paths are intended allocation until their implementation is delivered.

| Area | Physical owner | Focused map |
| --- | --- | --- |
| Production package and entry points | `src/archive_line_index/` | [Source ownership](layout/src.md) |
| Unit, integration and installed-artifact checks | `tests/` | [Test ownership](layout/tests.md) |
| Product documentation, governing design/contracts and evidence | Root Markdown and `docs/` | [Document ownership](layout/docs.md) |
| Build/version/tool configuration | Root `pyproject.toml` | This root |
| Release-artifact inventory validation | `scripts/check_release_artifacts.py`, checked by `tests/unit/test_release_artifacts.py` | This root and test map |
| Generated packages/checksums | Ignored `dist/` | This root |

## Root and packaging

`pyproject.toml` owns distribution name, Python/runtime requirements, static package version, Hatchling build selection, console-entry metadata and development-tool settings. The package uses the existing `src` import layout; production imports must not depend on repository-relative working directories. Root `README.md` owns installation/quick usage, `LICENSE` owns licensing, and root AGENTS/SDD/discovery/disclosure files retain their established instruction or attribution roles.

The release inventory checker owns deterministic validation of native wheel/sdist names, tag/project/version agreement, archive contents and checksum entries. It consumes built artifacts and version metadata without performing hosted publication or containing credentials. Native candidate names are `archive_line_index-{version}-py3-none-any.whl` and `archive_line_index-{version}.tar.gz`, with a generated `SHA256SUMS`; actual archive metadata must agree with the name and requested tag. The [phase release policy](PLAN.md) governs publication and hosted-byte readback.

The wheel contains the delivered package and distribution metadata. The source distribution contains production source, build configuration, license, README and selected test/support files, verification helpers and referenced documentation/notices needed for source verification/rebuild. Vendored agent plugins, conversation logs, credentials, caches and prior build outputs are excluded from distribution contents. Hatchling include/exclude rules and inventory checks enforce this boundary; the repository's whole tracked tree is not the package inventory.

`dist/`, coverage/tool caches, bytecode and test-generated archives/databases are generated work, not committed inputs. Root `.gitignore` owns exclusions, including the established credential exclusion. Release notes are finalized in root `RELEASE-NOTES.md`; Git/provider history retains prior release versions without requiring a second executable checklist.

## Placement rules

Production components import their owning modules, never public package initialization. Format dependencies stay in their adapters; only the 7z adapter imports `py7zr`. The scanner consumes its readable protocol, persistence consumes the offset model, and the CLI composes providers without being imported by core modules. The source map makes these directions concrete.

Tests have their own helpers and generated fixtures. Production cannot import `tests`, `scripts`, documentation tooling or installed-package test infrastructure. Tests for declarations live with the implementing owner; composed workflows and real dependency/filesystem behavior live under integration ownership. Documentation remains outside both source and tests, with links to canonical declarations/contracts instead of copied normative definitions.

Source, test and document maps are separate children with one physical owner for each subject. New files require a clear fit to these responsibilities; a legitimate new home is reconciled through layout before dependent task scope relies on it. This map creates no public extension framework or speculative component beyond the accepted design.
