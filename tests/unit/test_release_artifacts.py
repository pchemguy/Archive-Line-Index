"""Synthetic native inventory faults precede real candidate validation."""

from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest
from scripts.check_release_artifacts import check_release_artifacts

PROJECT = 'name = "archive-line-index"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
METADATA = b"Metadata-Version: 2.4\nName: archive-line-index\nVersion: 0.1.0\nRequires-Python: >=3.11\n"


@pytest.fixture
def inventory(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "pyproject.toml"
    project.write_text("[project]\n" + PROJECT)
    dist = tmp_path / "dist"
    dist.mkdir()
    write_candidates(dist)
    return dist, project


def write_candidates(
    dist: Path,
    *,
    extra: str | None = None,
    family: str = "wheel",
    metadata: bytes = METADATA,
    source_project: str = PROJECT,
    entry_points: bytes | None = None,
) -> None:
    package = {
        "archive_line_index/__init__.py": b'"""Package."""\n',
        "archive_line_index/py.typed": b"",
    }
    wheel_entries = dict(package)
    info = "archive_line_index-0.1.0.dist-info/"
    wheel_entries.update(
        {
            info + "METADATA": metadata,
            info
            + "WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            info + "RECORD": b"",
        }
    )
    if entry_points is not None:
        wheel_entries[info + "entry_points.txt"] = entry_points
    source_entries = {"src/" + name: data for name, data in package.items()}
    source_entries.update(
        {
            "pyproject.toml": ("[project]\n" + source_project).encode(),
            "PKG-INFO": metadata,
            "README.md": b"# Package\n",
            "LICENSE": b"license\n",
        }
    )
    if extra:
        (wheel_entries if family == "wheel" else source_entries)[extra] = b"unsafe"
    with zipfile.ZipFile(
        dist / "archive_line_index-0.1.0-py3-none-any.whl", "w"
    ) as archive:
        for name, data in wheel_entries.items():
            archive.writestr(name, data)
    with tarfile.open(dist / "archive_line_index-0.1.0.tar.gz", "w:gz") as archive:
        for name, data in source_entries.items():
            member = tarfile.TarInfo("archive_line_index-0.1.0/" + name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


def test_valid_inventory_checksum_roundtrip(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    with pytest.raises(ValueError, match="SHA256SUMS"):
        check_release_artifacts(dist, project, "v0.1.0")
    hashes = check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    assert len(hashes) == 2 and all(len(v) == 64 for v in hashes.values())
    assert check_release_artifacts(dist, project, "v0.1.0") == hashes


@pytest.mark.parametrize(
    "bad",
    [
        ".agents/plugin/file.py",
        "docs/ai-logs/chat.md",
        "gh.tkn",
        "nested/.env",
        "__pycache__/a.pyc",
        "dist/old.whl",
        "../escape",
        "/absolute",
        "C:\\secret",
    ],
)
@pytest.mark.parametrize("family", ["wheel", "source"])
def test_unsafe_entries_rejected(
    inventory: tuple[Path, Path], bad: str, family: str
) -> None:
    dist, project = inventory
    write_candidates(dist, extra=bad, family=family)
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    assert not (dist / "SHA256SUMS").exists()


@pytest.mark.parametrize("tag", ["v0.2.0", "0.1.0", "v0.1.0-extra"])
def test_tag_must_match_static_version(inventory: tuple[Path, Path], tag: str) -> None:
    dist, project = inventory
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, tag, write_checksums=True)


def test_metadata_and_source_project_mismatch(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    write_candidates(
        dist, metadata=METADATA.replace(b"Version: 0.1.0", b"Version: 9.0.0")
    )
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    write_candidates(dist, source_project=PROJECT.replace("0.1.0", "9.0.0"))
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)


def test_missing_or_renamed_native_artifact(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    wheel = next(dist.glob("*.whl"))
    wheel.rename(dist / "renamed.whl")
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)


def test_checksum_tampering_and_extra_files(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    p = dist / "SHA256SUMS"
    p.write_text(p.read_text().replace(p.read_text()[:64], "0" * 64))
    with pytest.raises(ValueError, match="checksum"):
        check_release_artifacts(dist, project, "v0.1.0")
    (dist / "unexpected.zip").write_bytes(b"x")
    with pytest.raises(ValueError):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)


def test_source_and_wheel_package_bytes_must_agree(
    inventory: tuple[Path, Path],
) -> None:
    dist, project = inventory
    with zipfile.ZipFile(next(dist.glob("*.whl")), "a") as archive:
        archive.writestr("archive_line_index/extra.py", b"extra")
    with pytest.raises(ValueError, match="package"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)


def test_archive_special_entries_and_duplicates(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    wheel = next(dist.glob("*.whl"))
    with zipfile.ZipFile(wheel, "a") as archive:
        link = zipfile.ZipInfo("archive_line_index/link")
        link.external_attr = 0o120777 << 16
        archive.writestr(link, b"target")
    with pytest.raises(ValueError, match="special"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    write_candidates(dist)
    with (
        zipfile.ZipFile(wheel, "a") as archive,
        pytest.warns(UserWarning, match="Duplicate"),
    ):
        archive.writestr("archive_line_index/py.typed", b"")
    with pytest.raises(ValueError, match="Duplicate"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    write_candidates(dist)
    source = next(dist.glob("*.tar.gz"))
    with tarfile.open(source, "w:gz") as archive:
        link = tarfile.TarInfo("archive_line_index-0.1.0/link")
        link.type = tarfile.SYMTYPE
        link.linkname = "outside"
        archive.addfile(link)
    with pytest.raises(ValueError, match="special"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)


def test_inventory_symlink_rejected(inventory: tuple[Path, Path]) -> None:
    dist, project = inventory
    checksum = dist / "SHA256SUMS"
    try:
        checksum.symlink_to(project)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with pytest.raises(ValueError, match="ordinary"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    assert project.read_text().startswith("[project]")


@pytest.mark.parametrize("fault", ["absent", "stale", "source"])
def test_console_script_declaration_must_match(
    inventory: tuple[Path, Path], fault: str
) -> None:
    dist, project = inventory
    target = "archive_line_index.cli:main"
    old_target = "removed_package.cli:main"
    declared = PROJECT + f'\n[project.scripts]\narchive-line-index = "{target}"\n'
    project.write_text("[project]\n" + declared)
    entry_points = f"[console_scripts]\narchive-line-index = {target}\n".encode()
    write_candidates(dist, source_project=declared, entry_points=entry_points)
    assert (
        len(check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)) == 2
    )
    (dist / "SHA256SUMS").unlink()

    if fault == "source":
        declared = declared.replace(target, old_target)
    elif fault == "stale":
        entry_points = entry_points.replace(target.encode(), old_target.encode())
    write_candidates(
        dist,
        source_project=declared,
        entry_points=None if fault == "absent" else entry_points,
    )
    with pytest.raises(ValueError, match="console scripts"):
        check_release_artifacts(dist, project, "v0.1.0", write_checksums=True)
    assert not (dist / "SHA256SUMS").exists()
