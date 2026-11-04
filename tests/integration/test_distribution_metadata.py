"""Native artifact metadata and source rebuild input selection."""

import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_native_distribution_metadata_and_inventory(built_distributions: Path) -> None:
    wheel = built_distributions / "archive_line_index-0.3.0-py3-none-any.whl"
    source = built_distributions / "archive_line_index-0.3.0.tar.gz"
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = BytesParser().parsebytes(
            archive.read("archive_line_index-0.3.0.dist-info/METADATA")
        )
        assert "archive_line_index/py.typed" in names
        assert all(
            n.startswith(("archive_line_index/", "archive_line_index-0.3.0.dist-info/"))
            for n in names
        )
    assert metadata["Name"] == "archive-line-index"
    assert metadata["Version"] == "0.3.0"
    assert metadata["Requires-Python"] == ">=3.11"
    assert "py7zr" in metadata.get_all("Requires-Dist")
    with tarfile.open(source) as archive:
        names = archive.getnames()
    assert not any(
        "/.agents/" in n or "/ai-logs/" in n or n.endswith(".tkn") for n in names
    )
    for required in (
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "src/archive_line_index/__init__.py",
        "tests/unit/test_scanner.py",
        "AI_DISCLOSURE.md",
        "SDD-MANAGER.md",
    ):
        assert "archive_line_index-0.3.0/" + required in names
