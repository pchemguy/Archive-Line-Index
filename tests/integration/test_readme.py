"""Executable coverage for the user README."""

from __future__ import annotations

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).parents[2]
README = PROJECT_ROOT / "README.md"


def test_readme_covers_the_package_contract() -> None:
    text = README.read_text(encoding="utf-8")

    required_phrases = {
        "# Archive Line Index",
        "## Installation",
        "## Stream content",
        "## Build an in-memory index",
        "## Persist an index",
        "EOF sentinel",
        "owns and closes",
        "successful terminal EOF",
        "decompressed byte offsets",
        "random seek",
        "source identity",
        "memory mapping",
        "encrypted archives",
        "command-line interface",
    }
    assert all(phrase in text for phrase in required_phrases)
    assert all(format_name in text for format_name in ("plain", "ZIP", "TAR", "7z"))


def test_readme_development_links_resolve() -> None:
    text = README.read_text(encoding="utf-8")
    expected = {
        "docs/dev/SPEC.md",
        "docs/dev/PLAN.md",
        "docs/dev/layout.md",
    }
    linked = set(re.findall(r"\[[^]]+\]\((docs/dev/[^)]+)\)", text))

    assert expected <= linked
    assert all((PROJECT_ROOT / target).is_file() for target in expected)


def test_every_python_example_executes(tmp_path, monkeypatch) -> None:
    text = README.read_text(encoding="utf-8")
    examples = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)
    assert len(examples) == 3
    monkeypatch.chdir(tmp_path)

    for position, example in enumerate(examples, start=1):
        namespace = {"__name__": f"readme_example_{position}"}
        exec(compile(example, f"README.md example {position}", "exec"), namespace)
