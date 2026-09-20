"""Plain-source adapter for the internal backend reader contract."""

from __future__ import annotations

import os

from ..sources import SourceHandle


class PlainBackendReader:
    """Expose a normalized source as a sequential backend reader."""

    def __init__(self, source: SourceHandle) -> None:
        self._source = source
        self._completed = False
        self._closed = False
        self._declared_size = self._measure_size(source)

    @property
    def declared_size(self) -> int | None:
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

        data = self._source.read(size)
        if not data:
            self._completed = True
        return data

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._source.close()

    @staticmethod
    def _measure_size(source: SourceHandle) -> int | None:
        if not source.seekable():
            return None
        position = source.tell()
        end = source.seek(0, os.SEEK_END)
        source.seek(position, os.SEEK_SET)
        return end


def open_plain_backend(source: SourceHandle) -> PlainBackendReader:
    """Construct a plain backend reader for ``source``."""

    return PlainBackendReader(source)
