"""Integration coverage for the installed package import surface."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import pkgutil

import archive_line_index


PUBLIC_NAMES = {
    "ArchiveLineIndexError",
    "ArchiveStructureError",
    "ContentStream",
    "DEFAULT_BUFFER_SIZE",
    "ExtractionError",
    "InvalidArchiveError",
    "InvalidIndexError",
    "PersistenceError",
    "SizeLimitExceededError",
    "Source",
    "UnsupportedFormatError",
    "build_line_index",
    "open_content_stream",
    "read_raw_index",
    "read_sqlite_index",
    "scan_line_offsets",
    "write_raw_index",
    "write_sqlite_index",
}

INTERNAL_NAMES = {
    "BackendReader",
    "DETECTION_PREFIX_SIZE",
    "MAX_OFFSET",
    "PlainBackendReader",
    "SevenZipBackendReader",
    "SourceFormat",
    "TarBackendReader",
    "ZipBackendReader",
    "_Completion",
    "_Failure",
    "_Payload",
    "_QueueProducer",
    "_QueueWriter",
    "_SelectedWriterFactory",
    "detect_format",
    "line_count",
    "line_range",
    "make_offset_array",
    "open_backend",
    "validate_offset_array",
}


def test_package_exports_exact_documented_public_surface() -> None:
    assert set(archive_line_index.__all__) == PUBLIC_NAMES
    assert all(hasattr(archive_line_index, name) for name in PUBLIC_NAMES)
    assert INTERNAL_NAMES.isdisjoint(vars(archive_line_index))


def test_every_package_submodule_imports_without_a_cycle() -> None:
    discovered = {
        module.name
        for module in pkgutil.walk_packages(
            archive_line_index.__path__,
            prefix=f"{archive_line_index.__name__}.",
        )
    }

    imported = {importlib.import_module(name).__name__ for name in discovered}

    assert imported == discovered


def test_internal_modules_do_not_import_through_package_root() -> None:
    package_root = Path(archive_line_index.__file__).parent
    violations: list[str] = []

    for module_path in package_root.rglob("*.py"):
        if module_path == package_root / "__init__.py":
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            imports_root = (
                isinstance(node, ast.Import)
                and any(
                    alias.name == archive_line_index.__name__
                    for alias in node.names
                )
            ) or (
                isinstance(node, ast.ImportFrom)
                and node.module == archive_line_index.__name__
            )
            if imports_root:
                relative = module_path.relative_to(package_root)
                violations.append(f"{relative}:{node.lineno}")

    assert violations == []
