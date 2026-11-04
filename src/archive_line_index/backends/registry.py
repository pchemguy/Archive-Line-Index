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
    if candidate.kind == FormatKind.ZIP:
        from .zip import open_zip_backend

        return open_zip_backend(path)
    if candidate.kind == FormatKind.TAR:
        from .tar import open_tar_backend

        return open_tar_backend(path)
    if candidate.kind == FormatKind.SEVEN_Z:
        try:
            from .sevenzip import open_7z_backend
        except ImportError as error:
            raise UnsupportedFormatError("7z dependency is unavailable") from error

        return open_7z_backend(path)
    raise UnsupportedFormatError(
        f"{candidate.kind.value} delivery is not implemented yet"
    )
