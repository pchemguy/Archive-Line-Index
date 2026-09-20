"""Source normalization, ownership, and detection-prefix replay."""

from __future__ import annotations

import io
import os
from os import PathLike
from typing import BinaryIO, TypeAlias


Source: TypeAlias = str | PathLike[str] | BinaryIO


class SourceHandle:
    """Package-controlled view over a path-owned or caller-owned byte stream.

    Seekable streams are presented relative to their position at attachment,
    making that position offset zero.  A detection prefix consumed from a
    non-seekable stream is retained and replayed by subsequent reads.
    """

    def __init__(self, stream: BinaryIO, *, owned: bool) -> None:
        self._stream = stream
        self._owned = owned
        self._closed = False
        self._replay = bytearray()
        self._probe_complete = False

        probe = self._read_direct(0)
        if probe != b"":
            raise TypeError("a zero-length binary read must return b''")

        try:
            self._seekable = bool(stream.seekable())
        except (AttributeError, OSError):
            self._seekable = False

        if self._seekable:
            try:
                self._origin = stream.tell()
            except (AttributeError, OSError) as exc:
                raise TypeError(
                    "a seekable source must provide a working tell()"
                ) from exc
        else:
            self._origin = None

    @property
    def owned(self) -> bool:
        """Whether the package owns the underlying stream."""

        return self._owned

    @property
    def closed(self) -> bool:
        """Whether this handle has been released."""

        return self._closed

    def readable(self) -> bool:
        """Return whether this open handle supports byte reads."""

        return not self._closed

    def seekable(self) -> bool:
        """Return whether relative positioning is available."""

        return not self._closed and self._seekable

    def tell(self) -> int:
        """Return the position relative to the attachment origin."""

        self._check_open()
        if not self._seekable or self._origin is None:
            raise io.UnsupportedOperation("source is not seekable")
        return self._stream.tell() - self._origin

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        """Seek relative to the attachment origin and return that position."""

        self._check_open()
        if not self._seekable or self._origin is None:
            raise io.UnsupportedOperation("source is not seekable")
        if whence == os.SEEK_SET:
            absolute = self._stream.seek(self._origin + offset, os.SEEK_SET)
        elif whence in (os.SEEK_CUR, os.SEEK_END):
            absolute = self._stream.seek(offset, whence)
        else:
            raise ValueError(f"invalid whence: {whence}")
        return absolute - self._origin

    def read(self, size: int = -1) -> bytes:
        """Read bytes, replaying a non-seekable detection prefix first."""

        self._check_open()
        if not isinstance(size, int):
            raise TypeError("size must be an integer")
        if size == 0:
            return b""

        if size < 0:
            prefix = bytes(self._replay)
            self._replay.clear()
            return prefix + self._read_direct(-1)

        prefix_size = min(size, len(self._replay))
        prefix = bytes(self._replay[:prefix_size])
        del self._replay[:prefix_size]
        remaining = size - prefix_size
        if remaining == 0:
            return prefix
        return prefix + self._read_direct(remaining)

    def probe_prefix(self, size: int) -> bytes:
        """Read a bounded detection prefix without losing processing bytes."""

        self._check_open()
        if not isinstance(size, int) or isinstance(size, bool):
            raise TypeError("prefix size must be an integer")
        if size < 0:
            raise ValueError("prefix size must be non-negative")
        if self._probe_complete:
            raise RuntimeError("the source prefix has already been probed")

        prefix = bytearray()
        while len(prefix) < size:
            chunk = self._read_direct(size - len(prefix))
            if not chunk:
                break
            prefix.extend(chunk)

        if self._seekable:
            self.seek(0)
        else:
            self._replay.extend(prefix)
        self._probe_complete = True
        return bytes(prefix)

    def close(self) -> None:
        """Release the handle and close only package-owned streams."""

        if self._closed:
            return
        self._closed = True
        self._replay.clear()
        if self._owned:
            self._stream.close()

    release = close

    def _check_open(self) -> None:
        if self._closed:
            raise ValueError("I/O operation on closed source")

    def _read_direct(self, size: int) -> bytes:
        data = self._stream.read(size)
        if not isinstance(data, bytes):
            raise TypeError("source stream read() must return bytes")
        return data


def open_source(source: Source) -> SourceHandle:
    """Normalize a filesystem path or caller-owned binary stream."""

    if isinstance(source, (str, os.PathLike)):
        path = os.fspath(source)
        if not isinstance(path, str):
            raise TypeError("source paths must resolve to str, not bytes")
        stream = open(path, "rb")
        try:
            return SourceHandle(stream, owned=True)
        except BaseException:
            stream.close()
            raise

    if not hasattr(source, "read"):
        raise TypeError("source must be a path or readable binary stream")
    return SourceHandle(source, owned=False)
