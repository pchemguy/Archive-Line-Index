"""Backend dispatch for detected source formats."""

from __future__ import annotations

from ..errors import UnsupportedFormatError
from ..formats import SourceFormat
from .base import BackendReader
from .plain import open_plain_backend
from .sevenzip import open_sevenzip_backend
from .tar import open_tar_backend
from .zip import open_zip_backend


def open_backend(
    source_format: SourceFormat,
    path: str,
) -> BackendReader:
    """Open the backend registered for ``source_format``."""

    if not isinstance(source_format, SourceFormat):
        raise TypeError("source_format must be a SourceFormat")
    if source_format is SourceFormat.PLAIN:
        return open_plain_backend(path)
    if source_format is SourceFormat.ZIP:
        return open_zip_backend(path)
    if source_format is SourceFormat.TAR:
        return open_tar_backend(path)
    if source_format is SourceFormat.SEVEN_ZIP:
        return open_sevenzip_backend(path)
    raise UnsupportedFormatError(
        f"{source_format.value} archive support is not available"
    )
