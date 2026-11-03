"""Small actual TAR fixtures; tests choose exposed member kinds and order."""

import io
import tarfile
from pathlib import Path


def make_tar(
    path: Path,
    entries: list[tuple[str, bytes, bytes]],
    *,
    mode: str = "w",
    format: int = tarfile.PAX_FORMAT,
) -> Path:
    """Write archive bytes without extracting any member paths."""
    with tarfile.open(path, mode, format=format) as archive:
        for name, data, kind in entries:
            info = tarfile.TarInfo(name)
            info.type = kind
            if kind in (tarfile.LNKTYPE, tarfile.SYMTYPE):
                info.linkname = "target"
            info.size = len(data) if info.isreg() else 0
            archive.addfile(info, io.BytesIO(data) if info.isreg() else None)
    return path
