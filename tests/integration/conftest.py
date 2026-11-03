"""Session-scoped native builds and clean installed runtime environments."""

from __future__ import annotations

import os
import shutil
import sys
import tarfile
import venv
from pathlib import Path

import pytest
from tests.helpers.packaging import InstalledPackage, run_checked


@pytest.fixture(scope="session")
def built_distributions(tmp_path_factory: pytest.TempPathFactory) -> Path:
    repo = Path(__file__).resolve().parents[2]
    dist = tmp_path_factory.mktemp("native-dist")
    run_checked(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(dist)], repo
    )
    return dist


@pytest.fixture(scope="session")
def rebuilt_wheel(
    built_distributions: Path, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    source = tmp_path_factory.mktemp("sdist-source")
    with tarfile.open(next(built_distributions.glob("*.tar.gz"))) as archive:
        archive.extractall(source, filter="data")
    project = next(p for p in source.iterdir() if p.is_dir())
    out = tmp_path_factory.mktemp("rebuilt-dist")
    run_checked(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(out),
        ],
        project,
    )
    return next(out.glob("*.whl"))


@pytest.fixture(scope="session", params=["wheel", "rebuilt-sdist"])
def installed_package(
    request: pytest.FixtureRequest,
    built_distributions: Path,
    rebuilt_wheel: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> InstalledPackage:
    artifact = (
        next(built_distributions.glob("*.whl"))
        if request.param == "wheel"
        else rebuilt_wheel
    )
    root = tmp_path_factory.mktemp("installed-" + str(request.param))
    prefix = root / "runtime"
    uv = shutil.which("uv")
    bundled_uv = Path(sys.base_prefix) / "bin" / "uv"
    if uv is None and bundled_uv.is_file():
        uv = str(bundled_uv)
    venv.EnvBuilder(with_pip=uv is None).create(prefix)
    python = prefix / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if uv is not None:
        run_checked(
            [uv, "pip", "install", "--python", str(python), str(artifact)], root
        )
    else:
        run_checked([str(python), "-m", "pip", "install", str(artifact)], root)
    workdir = root / "consumer"
    workdir.mkdir()
    return InstalledPackage(python, workdir, artifact)
