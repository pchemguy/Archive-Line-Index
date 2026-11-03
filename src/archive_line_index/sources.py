"""Text filesystem source normalization without acquisition."""

import os
from pathlib import Path
from typing import TypeAlias

Source: TypeAlias = str | os.PathLike[str]


def normalize_source(source: Source) -> Path:
    """Return a path for a text filesystem source without opening it.

    Args:
        source: A string or path-like object returning a string.

    Raises:
        TypeError: If the filesystem representation is not text.
    """
    value = os.fspath(source)
    if not isinstance(value, str):
        raise TypeError("source must be a text filesystem path")
    return Path(value)
