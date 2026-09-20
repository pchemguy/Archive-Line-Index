"""Backend dispatch for detected source formats."""

from __future__ import annotations

from ..errors import UnsupportedFormatError
from ..formats import SourceFormat
from ..sources import SourceHandle
from .base import BackendReader
from .plain import open_plain_backend


def open_backend(
    source_format: SourceFormat,
    source: SourceHandle,
) -> BackendReader:
    """Open the backend registered for ``source_format``."""

    if not isinstance(source_format, SourceFormat):
        raise TypeError("source_format must be a SourceFormat")
    if source_format is SourceFormat.PLAIN:
        return open_plain_backend(source)
    raise UnsupportedFormatError(
        f"{source_format.value} archive support is not available"
    )
