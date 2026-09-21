"""Plain-path adapter for the internal backend reader contract."""

from __future__ import annotations

import os
from typing import BinaryIO


class PlainBackendReader:
    """Expose a package-owned plain file as a sequential backend reader."""

    def __init__(self, path: str) -> None:
        self._stream: BinaryIO = open(path, "rb")
        self._completed = False
        self._closed = False
        try:
            self._declared_size = os.fstat(self._stream.fileno()).st_size
        except BaseException:
            self._stream.close()
            raise

    @property
    def declared_size(self) -> int:
        return self._declared_size

    @property
    def completed(self) -> bool:
        return self._completed

    def read(self, size: int) -> bytes:
        if self._closed:
            raise ValueError("I/O operation on closed backend")
        if not isinstance(size, int) or isinstance(size, bool):
            raise TypeError("backend read size must be an integer")
        if size <= 0:
            raise ValueError("backend read size must be positive")
        if self._completed:
            return b""

        data = self._stream.read(size)
        if not data:
            self._completed = True
        return data

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._stream.close()


def open_plain_backend(path: str) -> PlainBackendReader:
    """Open ``path`` as an uncompressed sequential source."""

    return PlainBackendReader(path)
