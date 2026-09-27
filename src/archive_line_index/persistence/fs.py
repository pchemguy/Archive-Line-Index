from __future__ import annotations

import os
from os import PathLike
from pathlib import Path


def _publish(temporary: Path, destination: Path, *, overwrite: bool) -> None:
    if overwrite:
        os.replace(temporary, destination)
        return
    if destination.exists():
        raise FileExistsError(destination)
    os.link(temporary, destination)
    temporary.unlink()


def _normalize_path(value: str | PathLike[str], name: str) -> Path:
    if not isinstance(value, (str, os.PathLike)):
        raise TypeError(f"{name} must be a filesystem path")
    path = os.fspath(value)
    if not isinstance(path, str):
        raise TypeError(f"{name} paths must resolve to str, not bytes")
    return Path(path)
