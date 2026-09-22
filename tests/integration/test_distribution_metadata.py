"""Checks for the source distribution's declarative package metadata."""

from __future__ import annotations

from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).parents[2]


def load_pyproject() -> dict:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
        return tomllib.load(stream)


def test_distribution_metadata_describes_supported_runtime() -> None:
    metadata = load_pyproject()["project"]

    assert metadata["name"] == "archive-line-index"
    assert metadata["version"] == "0.1.0"
    assert metadata["readme"] == "README.md"
    assert metadata["license"] == "MIT"
    assert metadata["license-files"] == ["LICENSE"]
    assert metadata["requires-python"] == ">=3.11"
    assert metadata["dependencies"] == ["py7zr>=1.1,<1.2"]
    assert set(metadata["keywords"]) >= {
        "7z",
        "archive",
        "indexing",
        "streaming",
    }

    classifiers = set(metadata["classifiers"])
    assert "Operating System :: OS Independent" in classifiers
    assert "Programming Language :: Python :: 3.11" in classifiers
    assert "Programming Language :: Python :: 3.12" in classifiers
    assert "Programming Language :: Python :: 3.13" in classifiers
    assert "Programming Language :: Python :: 3.14" in classifiers


def test_build_metadata_uses_explicit_src_package_discovery() -> None:
    configuration = load_pyproject()

    assert configuration["build-system"]["requires"] == [
        "setuptools>=77",
        "wheel",
    ]
    assert configuration["tool"]["setuptools"]["packages"]["find"] == {
        "where": ["src"],
        "include": ["archive_line_index*"],
        "namespaces": False,
    }
    assert configuration["project"]["optional-dependencies"]["test"] == [
        "pytest>=8,<10"
    ]


def test_declared_license_and_readme_files_exist() -> None:
    assert (PROJECT_ROOT / "LICENSE").is_file()
    assert (PROJECT_ROOT / "README.md").is_file()
