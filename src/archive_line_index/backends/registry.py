"""Explicit adapter selection without premature archive support claims."""

from pathlib import Path

from ..errors import UnsupportedFormatError
from ..formats import FormatCandidate, FormatKind
from .base import BackendReader
from .plain import open_plain_backend


def open_backend(path: Path, candidate: FormatCandidate) -> BackendReader:
    """Open the selected delivered adapter, never reinterpret archive claims."""
    if candidate.kind == FormatKind.PLAIN:
        return open_plain_backend(path)
    raise UnsupportedFormatError(
        f"{candidate.kind.value} delivery is not implemented yet"
    )
