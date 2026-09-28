"""Canonical in-memory line-offset representation and invariants."""

from __future__ import annotations

import itertools
from array import array
from collections.abc import Iterable

from .errors import InvalidIndexError

MAX_OFFSET = (1 << 63) - 1


def make_offset_array(values: Iterable[int]) -> array:
    """Construct and validate a canonical unsigned 64-bit offset array."""

    try:
        iterator = iter(values)
    except TypeError:
        raise TypeError("values must be an iterable") from None

    chained: Iterable[int]
    try:
        first = next(iterator)
    except StopIteration:
        chained = ()
    else:
        if type(first) is bool:
            raise InvalidIndexError("offsets must be integers")
        try:
            second = next(iterator)
        except StopIteration:
            chained = (first,)
        else:
            if type(second) is bool:
                raise InvalidIndexError("offsets must be integers")
            chained = itertools.chain((first, second), iterator)

    try:
        offsets = array("Q", chained)
    except TypeError as e:
        raise InvalidIndexError("offsets must be integers") from e
    except OverflowError as e:
        raise InvalidIndexError("offset is outside the supported range") from e

    return validate_offset_array(offsets)


def validate_offset_array(offsets: object) -> array:
    """Validate and return a canonical ``array('Q')`` offset sequence."""

    if not isinstance(offsets, array):
        raise InvalidIndexError("offset sequence must be an array")
    if offsets.typecode != "Q":
        raise InvalidIndexError("offset array type code must be 'Q'")
    if offsets.itemsize != 8:
        raise InvalidIndexError("offset array items must be eight bytes")
    if not offsets:
        raise InvalidIndexError("offset array must contain an EOF sentinel")
    if offsets[0] not in (0, 3):
        raise InvalidIndexError("first offset must be 0 or 3")

    previous: int | None = None
    for value in offsets:
        if value > MAX_OFFSET:
            raise InvalidIndexError("offset exceeds the shared SQLite range")
        if previous is not None and value <= previous:
            raise InvalidIndexError("offsets must be strictly increasing")
        previous = value
    return offsets


def line_count(offsets: object) -> int:
    """Return the number of indexed lines after structural validation."""

    return len(validate_offset_array(offsets)) - 1


def line_range(offsets: object, line_number: int) -> tuple[int, int]:
    """Return the half-open byte range for one zero-based line number."""

    validated = validate_offset_array(offsets)
    if not isinstance(line_number, int) or isinstance(line_number, bool):
        raise TypeError("line_number must be an integer")
    count = len(validated) - 1
    if not 0 <= line_number < count:
        raise IndexError("line_number is outside the index")
    return validated[line_number], validated[line_number + 1]
