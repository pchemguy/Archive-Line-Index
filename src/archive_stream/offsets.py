"""Canonical unsigned eight-byte offsets within the shared signed range."""

from __future__ import annotations

from array import array

from .errors import InvalidIndexError

MAX_OFFSET = (1 << 63) - 1


def _validate_representation(offsets: array[int]) -> None:
    if (
        not isinstance(offsets, array)
        or offsets.typecode != "Q"
        or offsets.itemsize != 8
    ):
        raise TypeError('offsets must be an array("Q") with eight-byte items')


def check_position(value: int) -> None:
    """Reject unrepresentable byte coordinates before construction/publication."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= MAX_OFFSET
    ):
        raise InvalidIndexError(f"Offset {value!r} is outside 0..{MAX_OFFSET}")


def validate_offsets(offsets: array[int]) -> None:
    """Validate a completed canonical index without changing its borrowed array.

    Raises:
        TypeError: If the array representation is wrong.
        InvalidIndexError: If its contents are empty, unordered or out of range.
    """
    _validate_representation(offsets)
    if not offsets or offsets[0] not in (0, 3):
        raise InvalidIndexError("Completed offsets must begin with 0 or 3")
    previous = -1
    for value in offsets:
        check_position(value)
        if value <= previous:
            raise InvalidIndexError("Offsets must increase strictly")
        previous = value


def append_offset(offsets: array[int], value: int) -> None:
    """Append a checked coordinate during construction, permitting an empty array.

    This operation checks the new value and its boundary only; a builder must
    complete its sentinel before calling validate_offsets on the whole index.
    """
    _validate_representation(offsets)
    check_position(value)
    if not offsets:
        if value not in (0, 3):
            raise InvalidIndexError("Initial offset must be 0 or 3")
    elif value <= offsets[-1]:
        raise InvalidIndexError("Appended offset must increase strictly")
    offsets.append(value)
