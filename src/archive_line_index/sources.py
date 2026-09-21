"""Path-only source normalization."""

from __future__ import annotations

import os
from os import PathLike
from typing import TypeAlias


Source: TypeAlias = str | PathLike[str]


def normalize_source_path(source: Source) -> str:
    """Return a native string path without opening it."""

    if not isinstance(source, (str, os.PathLike)):
        raise TypeError("source must be a filesystem path")
    path = os.fspath(source)
    if not isinstance(path, str):
        raise TypeError("source paths must resolve to str, not bytes")
    return path
