"""Stable hosted bundles are independently validated against real native builds."""

import json
import sys
import zipfile
from pathlib import Path

import pytest
from scripts.prepare_release import ASSET_NAMES, check_bundles, prepare_bundles
from tests.helpers.packaging import run_checked

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_real_bundles_and_independent_cli(
    built_distributions: Path, tmp_path: Path, project_version: str
) -> None:
    repo = Path(__file__).resolve().parents[2]
    hashes = prepare_bundles(
        built_distributions,
        tmp_path / "release",
        repo / "pyproject.toml",
        "v" + project_version,
    )
    assert {p.name for p in (tmp_path / "release").iterdir()} == {
        "archive-stream-wheel.zip",
        "archive-stream-source.zip",
        "SHA256SUMS",
    }
    assert (
        check_bundles(
            tmp_path / "release", repo / "pyproject.toml", "v" + project_version
        )
        == hashes
    )
    result = run_checked(
        [
            sys.executable,
            "-m",
            "scripts.prepare_release",
            "--output",
            str(tmp_path / "release"),
            "--tag",
            "v" + project_version,
            "--check",
        ],
        repo,
    )
    assert json.loads(result) == hashes
    for asset in ASSET_NAMES[:2]:
        with zipfile.ZipFile(tmp_path / "release" / asset) as archive:
            assert len(archive.namelist()) == 1


@pytest.mark.parametrize(
    "fault",
    ["unknown-versioned", "case-collision", "tamper", "checksum", "extra-member"],
)
def test_release_inventory_faults_are_rejected(
    built_distributions: Path, tmp_path: Path, fault: str, project_version: str
) -> None:
    repo = Path(__file__).resolve().parents[2]
    output = tmp_path / "release"
    prepare_bundles(
        built_distributions, output, repo / "pyproject.toml", "v" + project_version
    )
    if fault == "unknown-versioned":
        (output / "surprise-v2.weird").write_bytes(b"x")
    elif fault == "case-collision":
        (output / ASSET_NAMES[0].upper()).write_bytes(b"x")
    elif fault == "checksum":
        (output / "SHA256SUMS").write_text("wrong")
    elif fault == "tamper":
        (output / ASSET_NAMES[0]).write_bytes(b"wrong")
    else:
        with zipfile.ZipFile(output / ASSET_NAMES[0], "a") as archive:
            archive.writestr("unexpected", b"extra")
    with pytest.raises((ValueError, zipfile.BadZipFile)):
        check_bundles(output, repo / "pyproject.toml", "v" + project_version)


@pytest.mark.parametrize("target_exists", [True, False], ids=["existing", "dangling"])
def test_symlink_output_is_rejected_before_any_write(
    built_distributions: Path,
    tmp_path: Path,
    project_version: str,
    target_exists: bool,
) -> None:
    repo = Path(__file__).resolve().parents[2]
    target = tmp_path / "external"
    if target_exists:
        target.mkdir()
    output = tmp_path / "release-link"
    try:
        output.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    before = {p.name: p.read_bytes() for p in built_distributions.iterdir()}
    with pytest.raises(ValueError, match="ordinary"):
        prepare_bundles(
            built_distributions, output, repo / "pyproject.toml", "v" + project_version
        )
    assert output.is_symlink()
    assert target.exists() == target_exists
    if target_exists:
        assert list(target.iterdir()) == []
    assert {p.name: p.read_bytes() for p in built_distributions.iterdir()} == before
