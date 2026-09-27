"""Executable integrity checks for development documentation and evidence."""

from __future__ import annotations

import ast
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).parents[2]
DEV_DOCS = PROJECT_ROOT / "docs" / "dev"
ACCEPTANCE = DEV_DOCS / "ACCEPTANCE.md"


def _heading_anchor(heading: str) -> str:
    """Return the GitHub-style anchor used by the project's simple headings."""

    lowered = heading.strip().lower().replace("`", "")
    return re.sub(r"[^\w -]", "", lowered).replace(" ", "-")


def _anchors(path: Path) -> set[str]:
    return {
        _heading_anchor(match.group(1))
        for match in re.finditer(
            r"^#{1,6}\s+(.+?)\s*$",
            path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    }


def test_all_local_markdown_links_resolve() -> None:
    documents = [PROJECT_ROOT / "README.md", *DEV_DOCS.rglob("*.md")]
    failures: list[str] = []

    for document in documents:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("mailto:"):
                continue
            path_text, _, fragment = target.partition("#")
            resolved = document if not path_text else document.parent / path_text
            resolved = resolved.resolve()
            if not resolved.is_file():
                failures.append(f"{document.relative_to(PROJECT_ROOT)} -> {target}")
                continue
            if fragment and fragment not in _anchors(resolved):
                failures.append(
                    f"{document.relative_to(PROJECT_ROOT)} -> {target} (missing anchor)"
                )

    assert failures == []


def test_acceptance_matrix_maps_every_normative_condition_to_evidence() -> None:
    specifications = {
        "SYS": (DEV_DOCS / "SPEC.md", "System acceptance conditions"),
        "ARCH": (DEV_DOCS / "spec/archive-handling.md", "Acceptance matrix"),
        "STREAM": (DEV_DOCS / "spec/content-stream.md", "Acceptance conditions"),
        "INDEX": (DEV_DOCS / "spec/line-index.md", "Acceptance conditions"),
        "PERSIST": (DEV_DOCS / "spec/persistence.md", "Acceptance conditions"),
        "API": (DEV_DOCS / "spec/public-api.md", "Public API acceptance conditions"),
    }
    expected = set()
    for prefix, (path, heading) in specifications.items():
        source = path.read_text(encoding="utf-8")
        section = re.search(
            rf"^## \d+\. {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
            source,
            flags=re.MULTILINE,
        )
        assert section is not None, path
        if prefix == "ARCH":
            # Archive cases use bullet points rather than a numbered list.
            count = len(re.findall(r"^- ", section.group(1), flags=re.MULTILINE))
        else:
            numbers = [
                int(number)
                for number in re.findall(
                    r"^(\d+)\. ", section.group(1), flags=re.MULTILINE
                )
            ]
            count = len(numbers)
            assert numbers == list(range(1, count + 1)), path
        assert count > 0, path
        expected.update(f"{prefix}-{number}" for number in range(1, count + 1))
    text = ACCEPTANCE.read_text(encoding="utf-8")
    matches = list(
        re.finditer(
            r"^\| (?P<identifier>[A-Z]+-\d+) \|.*?\| (?P<evidence>.*?) \|$",
            text,
            flags=re.MULTILINE,
        )
    )
    rows = {match.group("identifier"): match.group("evidence") for match in matches}

    assert len(matches) == len(rows)
    assert set(rows) == expected
    assert all("tests/" in evidence or "Manual:" in evidence for evidence in rows.values())


def test_acceptance_test_selectors_name_existing_tests() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    selectors = set(
        re.findall(r"(tests/[\w/]+\.py::test_[A-Za-z0-9_]+)", text)
    )
    assert selectors

    for selector in selectors:
        path_text, function_name = selector.split("::", 1)
        path = PROJECT_ROOT / path_text
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        assert function_name in functions, selector


def test_layout_nodes_cover_current_docs_source_and_tests() -> None:
    ownership = {
        DEV_DOCS / "layout" / "docs.md": sorted(DEV_DOCS.rglob("*.md")),
        DEV_DOCS / "layout" / "src.md": sorted(
            (PROJECT_ROOT / "src" / "archive_line_index").rglob("*.py")
        ),
        DEV_DOCS / "layout" / "tests.md": sorted(
            (PROJECT_ROOT / "tests").rglob("*.py")
        ),
    }
    failures: list[str] = []

    for owner, paths in ownership.items():
        owner_text = owner.read_text(encoding="utf-8")
        for path in paths:
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            if relative not in owner_text:
                failures.append(f"{relative} missing from {owner.relative_to(PROJECT_ROOT)}")

    assert failures == []


def test_obsolete_architecture_document_is_retired() -> None:
    assert not (PROJECT_ROOT / "docs" / "architecture.md").exists()
