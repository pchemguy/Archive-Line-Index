"""Independent raw little-endian offset arrays with protected publication."""

from __future__ import annotations

import errno
import os
import sys
from array import array
from typing import BinaryIO

from ..errors import InvalidIndexError
from ..offsets import validate_offsets
from ..sources import Source, normalize_source
from .fs import (
    flush_file,
    open_binary_file,
    publish_index_file,
    temporary_sibling,
    validate_destination,
)

_BYTEORDER = sys.byteorder


def _encode(offsets: array[int]) -> bytes:
    payload = offsets.tobytes()
    if _BYTEORDER == "big":
        converted = array("Q")
        converted.frombytes(payload)
        converted.byteswap()
        payload = converted.tobytes()
    return payload


def _write_all(handle: BinaryIO, payload: bytes) -> None:
    with memoryview(payload) as view:
        position = 0
        while position < len(view):
            count = handle.write(view[position:])
            if count is None or count <= 0 or count > len(view) - position:
                raise OSError(errno.EIO, "Incomplete raw index write")
            position += count


def write_raw_index(
    offsets: array[int], destination: Source, *, overwrite: bool = False
) -> None:
    """Store canonical offsets as headerless little-endian unsigned 64-bit values.

    Args:
        offsets: Borrowed canonical Q/eight-byte array, never modified.
        destination: Explicit text filesystem path.
        overwrite: Authorize atomic replacement; otherwise protect existing names.

    Validation precedes temporary allocation. A post-publication cleanup failure
    retains the completed destination and includes its path in an exception note.
    """
    validate_offsets(offsets)
    path = validate_destination(destination, overwrite=overwrite)
    payload = _encode(offsets)
    published = False
    try:
        with temporary_sibling(path) as temporary:
            with open_binary_file(temporary, "wb") as handle:
                _write_all(handle, payload)
                flush_file(handle)
                if os.fstat(handle.fileno()).st_size != len(payload):
                    raise OSError(errno.EIO, "Raw index size mismatch")
            publish_index_file(temporary, path, overwrite=overwrite)
            published = True
    except BaseException as error:
        if published:
            error.add_note(f"Publication already succeeded: {path}")
        raise


def read_raw_index(source: Source) -> array[int]:
    """Load a new canonical array from complete little-endian records.

    Empty/partial files and invalid offset contents raise InvalidIndexError.
    Ordinary filesystem errors retain their types. The input is never modified.
    """
    path = normalize_source(source)
    with open_binary_file(path, "rb") as handle:
        size = os.fstat(handle.fileno()).st_size
        if size == 0 or size % 8:
            raise InvalidIndexError(
                "Raw index must contain complete eight-byte records"
            )
        payload = handle.read()
        if len(payload) != size:
            raise InvalidIndexError("Incomplete raw index read")
    offsets = array("Q")
    if offsets.itemsize != 8:
        raise InvalidIndexError("Native unsigned Q offsets require eight-byte items")
    offsets.frombytes(payload)
    if _BYTEORDER == "big":
        offsets.byteswap()
    validate_offsets(offsets)
    return offsets
