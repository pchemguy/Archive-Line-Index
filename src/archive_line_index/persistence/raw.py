"""Headerless little-endian persistence for canonical line offsets."""

from __future__ import annotations

from array import array
import os
from os import PathLike
from pathlib import Path
import struct
import sys
import tempfile
from typing import BinaryIO

from ..errors import InvalidIndexError, PersistenceError
from ..offsets import validate_offset_array
from .fs import _normalize_path, _publish


def write_raw_index(
    offsets: array,
    destination: str | PathLike[str],
    *,
    overwrite: bool = False,
) -> None:
    """Write offsets as exact headerless little-endian unsigned integers."""

    validated = validate_offset_array(offsets)
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a bool")
    path = _normalize_path(destination, "destination")
    if not overwrite and path.exists():
        raise FileExistsError(path)

    data = _encode_little_endian(validated)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        _write_temporary(temporary, data)
        if temporary.stat().st_size != len(data):
            raise PersistenceError("raw index size validation failed")
        _publish(temporary, path, overwrite=overwrite)
    except BaseException as primary:
        try:
            temporary.unlink(missing_ok=True)
        except OSError as cleanup_error:
            primary.add_note(f"temporary cleanup failed: {cleanup_error}")
        raise


def read_raw_index(source: str | PathLike[str]) -> array:
    """Load and validate a complete raw little-endian offset file."""

    path = _normalize_path(source, "source")
    data = _read_bytes(path)
    if not data or len(data) % 8:
        raise InvalidIndexError(
            "raw index size must be a nonzero multiple of eight bytes"
        )
    return validate_offset_array(_decode_little_endian(data))


def _encode_little_endian(
    offsets: array,
    *,
    byteorder: str = sys.byteorder,
) -> bytes:
    if byteorder == "little":
        return offsets.tobytes()
    if byteorder == "big":
        copy = array("Q", offsets)
        copy.byteswap()
        return copy.tobytes()
    raise ValueError(f"unsupported byte order: {byteorder!r}")


def _decode_little_endian(
    data: bytes,
    *,
    byteorder: str = sys.byteorder,
) -> array:
    offsets = array("Q")
    offsets.frombytes(data)
    if byteorder == "little":
        return offsets
    if byteorder == "big":
        offsets.byteswap()
        return offsets
    raise ValueError(f"unsupported byte order: {byteorder!r}")


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _write_temporary(path: Path, data: bytes) -> None:
    with path.open("wb") as stream:
        _write_all(stream, data)
        stream.flush()
        os.fsync(stream.fileno())


def _write_all(stream: BinaryIO, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = stream.write(view[written:])
        if not isinstance(count, int) or count <= 0:
            raise PersistenceError("raw index write did not complete")
        written += count


