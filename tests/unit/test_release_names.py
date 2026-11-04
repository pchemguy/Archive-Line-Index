"""The actual release gate must reject version notation in every asset type."""

import json
from pathlib import Path

import pytest


def test_project_gate_runs_shared_contract_vectors() -> None:
    from scripts.release_names import check_names

    vectors = json.loads(
        (
            Path(__file__).resolve().parents[2] / "scripts/release-asset-cases.json"
        ).read_text()
    )
    check_names(vectors["valid"], vectors["valid"], vectors["release_version"])
    for marker in vectors["invalid_markers"]:
        for suffix in vectors["suffixes"]:
            name = "sample-" + marker + suffix
            with pytest.raises(ValueError):
                check_names([name], [name], vectors["release_version"])


@pytest.mark.parametrize(
    "names", [["package.zip", "PACKAGE.ZIP"], ["../package.zip"], ["package-v3"]]
)
def test_collisions_paths_and_single_component_versions_fail(names: list[str]) -> None:
    from scripts.release_names import check_names

    with pytest.raises(ValueError):
        check_names(names, names, "0.3.0")
