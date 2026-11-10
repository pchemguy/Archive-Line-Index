"""Bounded access to an owned ordinary binary file."""

import os
from pathlib import Path
from typing import BinaryIO

from .base import BackendReader, validate_positive_size


class _PlainReader:
    def __init__(self, handle: BinaryIO, size: int) -> None:
        self._handle = handle
        self.declared_size = size
        self.completed = False

    def read(self, size: int, /) -> bytes:
        validate_positive_size(size)
        data = self._handle.read(size)
        if not data:
            self.completed = True
        return data

    def close(self) -> None:
        self._handle.close()


def open_plain_backend(path: Path) -> BackendReader:
    """Open and own a file, releasing its handle if metadata acquisition fails."""
    handle = path.open("rb", buffering=0)
    try:
        return _PlainReader(handle, os.fstat(handle.fileno()).st_size)
    except BaseException as error:
        try:
            handle.close()
        except BaseException as cleanup:
            error.add_note(f"Source cleanup failed: {cleanup!r}")
        raise
