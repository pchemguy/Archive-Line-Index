"""Native artifact metadata and source rebuild input selection."""

import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_native_distribution_metadata_and_inventory(
    built_distributions: Path, project_version: str
) -> None:
    wheel = built_distributions / f"archive_stream-{project_version}-py3-none-any.whl"
    source = built_distributions / f"archive_stream-{project_version}.tar.gz"
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = BytesParser().parsebytes(
            archive.read(f"archive_stream-{project_version}.dist-info/METADATA")
        )
        assert "archive_stream/py.typed" in names
        entry_points = archive.read(
            f"archive_stream-{project_version}.dist-info/entry_points.txt"
        ).decode("utf-8")
        assert entry_points.splitlines() == [
            "[console_scripts]",
            "archive-line-index = archive_stream.cli:main",
        ]
        assert all(
            n.startswith(
                (
                    "archive_stream/",
                    f"archive_stream-{project_version}.dist-info/",
                )
            )
            for n in names
        )
    assert metadata["Name"] == "archive-stream"
    assert metadata["Version"] == project_version
    assert metadata["Requires-Python"] == ">=3.11"
    assert "py7zr<1.2,>=1.1.4" in metadata.get_all("Requires-Dist")
    with tarfile.open(source) as archive:
        names = archive.getnames()
    assert not any(
        "/.agents/" in n or "/ai-logs/" in n or n.endswith(".tkn") for n in names
    )
    for required in (
        "pyproject.toml",
        "README.md",
        "docs/API_REF.md",
        "LICENSE",
        "src/archive_stream/__init__.py",
        "tests/unit/test_scanner.py",
        "AI_DISCLOSURE.md",
        "SDD-MANAGER.md",
    ):
        assert f"archive_stream-{project_version}/" + required in names
