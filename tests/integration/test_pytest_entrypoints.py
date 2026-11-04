"""Checkout test imports do not rely on implicit current-directory insertion."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.parametrize(
    "outside_checkout", [False, True], ids=["safe-path", "outside"]
)
def test_release_tests_collect_without_implicit_checkout_import(
    tmp_path: Path, outside_checkout: bool
) -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        "tests/integration/test_release_artifacts.py",
        "tests/integration/test_release_bundles.py",
        "tests/unit/test_prepare_release.py",
        "tests/unit/test_release_artifacts.py",
    ]
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS"}
    }
    result = subprocess.run(
        [
            sys.executable,
            "-P",  # Like the console launcher, do not add cwd to sys.path.
            "-m",
            "pytest",
            "-c",
            str(root / "pyproject.toml"),
            "--collect-only",
            "-q",
            *[str(root / target) for target in targets],
        ],
        cwd=tmp_path if outside_checkout else root,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.integration
@pytest.mark.parametrize("disabled", ["asyncio", "timeout", "all"])
def test_missing_test_plugins_fail_with_clear_prerequisite(
    tmp_path: Path, disabled: str
) -> None:
    root = Path(__file__).resolve().parents[2]
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS"}
    }
    blocked = [] if disabled == "all" else ["-p", "no:" + disabled]
    if disabled == "all":
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            "pytest",
            "-c",
            str(root / "pyproject.toml"),
            *blocked,
            "--collect-only",
            str(root / "tests/integration/test_distribution_metadata.py"),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    diagnostic = result.stdout + result.stderr
    assert result.returncode == 4, diagnostic
    assert "Missing required plugins" in diagnostic
    for plugin in (
        ["pytest-asyncio", "pytest-timeout"]
        if disabled == "all"
        else ["pytest-" + disabled]
    ):
        assert plugin in diagnostic
    assert "PytestConfigWarning" not in diagnostic
    assert "PytestUnknownMarkWarning" not in diagnostic
