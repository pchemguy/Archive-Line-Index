"""Small generated archives used by backend and integration tests."""

from __future__ import annotations

import io
import stat
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import py7zr


MemberKind = Literal["file", "directory", "symlink", "hardlink", "fifo"]


@dataclass(frozen=True, slots=True)
class ArchiveMember:
    """Declarative test member independent of an archive implementation."""

    name: str
    data: bytes = b""
    kind: MemberKind = "file"
    target: str = ""


def write_zip(path: Path, members: Sequence[ArchiveMember]) -> Path:
    """Create a ZIP fixture without calling production package code."""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member in members:
            if member.kind == "file":
                archive.writestr(member.name, member.data)
            elif member.kind == "directory":
                name = member.name.rstrip("/") + "/"
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFDIR | 0o755) << 16
                archive.writestr(info, b"")
            elif member.kind == "symlink":
                info = zipfile.ZipInfo(member.name)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, member.target.encode())
            else:
                raise ValueError(f"ZIP cannot generate {member.kind!r} fixture")
    return path


def write_tar(path: Path, members: Sequence[ArchiveMember]) -> Path:
    """Create a TAR fixture, selecting compression from ``path``."""

    mode = _tar_write_mode(path)
    with tarfile.open(path, mode) as archive:
        for member in members:
            info = tarfile.TarInfo(member.name)
            if member.kind == "file":
                info.size = len(member.data)
                archive.addfile(info, io.BytesIO(member.data))
            elif member.kind == "directory":
                info.type = tarfile.DIRTYPE
                info.mode = 0o755
                archive.addfile(info)
            elif member.kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = member.target
                archive.addfile(info)
            elif member.kind == "hardlink":
                info.type = tarfile.LNKTYPE
                info.linkname = member.target
                archive.addfile(info)
            elif member.kind == "fifo":
                info.type = tarfile.FIFOTYPE
                archive.addfile(info)
            else:
                raise ValueError(f"unknown TAR member kind: {member.kind!r}")
    return path


def write_7z(
    path: Path,
    members: Sequence[ArchiveMember],
) -> Path:
    """Create a 7z fixture with files and explicit directory entries."""

    with tempfile.TemporaryDirectory() as directory:
        staging = Path(directory)
        with py7zr.SevenZipFile(path, "w") as archive:
            for index, member in enumerate(members):
                if member.kind == "file":
                    archive.writestr(member.data, member.name)
                elif member.kind == "directory":
                    source = staging / f"directory-{index}"
                    source.mkdir()
                    archive.write(source, arcname=member.name.rstrip("/"))
                else:
                    raise ValueError(
                        f"7z cannot portably generate {member.kind!r} fixture"
                    )
    return path


def _tar_write_mode(path: Path) -> str:
    lower_name = path.name.lower()
    if lower_name.endswith((".tar.gz", ".tgz")):
        return "w:gz"
    if lower_name.endswith((".tar.bz2", ".tbz2", ".tbz")):
        return "w:bz2"
    if lower_name.endswith((".tar.xz", ".txz")):
        return "w:xz"
    return "w:"
