"""The inventory helper accepts real native builds and has a usable CLI."""

import json
import sys
from pathlib import Path

import pytest
from scripts.check_release_artifacts import check_release_artifacts
from tests.helpers.packaging import run_checked

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_real_candidate_inventory_and_cli(built_distributions: Path) -> None:
    repo = Path(__file__).resolve().parents[2]
    hashes = check_release_artifacts(
        built_distributions, repo / "pyproject.toml", "v0.2.0", write_checksums=True
    )
    result = run_checked(
        [
            sys.executable,
            str(repo / "scripts/check_release_artifacts.py"),
            "--dist",
            str(built_distributions),
            "--pyproject",
            str(repo / "pyproject.toml"),
            "--tag",
            "v0.2.0",
        ],
        built_distributions,
    )
    assert json.loads(result) == hashes
