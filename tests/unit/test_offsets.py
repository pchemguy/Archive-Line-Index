"""Canonical completed arrays and separate checked construction."""

from array import array

import pytest

from archive_line_index.errors import InvalidIndexError
from archive_line_index.offsets import MAX_OFFSET, append_offset, validate_offsets


@pytest.mark.parametrize("values", [[0], [3], [0, 1], [3, 4, 10], [0, MAX_OFFSET]])
def test_valid_completed_offsets(values: list[int]) -> None:
    a = array("Q", values)
    validate_offsets(a)
    assert a.tolist() == values


@pytest.mark.parametrize(
    "values", [[], [1], [4], [0, 0], [3, 3], [0, 3, 2], [0, MAX_OFFSET + 1]]
)
def test_invalid_completed_contents(values: list[int]) -> None:
    with pytest.raises(InvalidIndexError):
        validate_offsets(array("Q", values))


@pytest.mark.parametrize("value", [[0, 1], array("q", [0, 1]), array("I", [0])])
def test_wrong_container_or_typecode(value: object) -> None:
    with pytest.raises(TypeError):
        validate_offsets(value)  # type: ignore[arg-type]


def test_checked_append_accepts_empty_construction_but_not_completed_empty() -> None:
    a = array("Q")
    append_offset(a, 3)
    append_offset(a, 9)
    validate_offsets(a)
    for value in [9, 8, MAX_OFFSET + 1, -1]:
        with pytest.raises(InvalidIndexError):
            append_offset(a, value)
        assert a.tolist() == [3, 9]
