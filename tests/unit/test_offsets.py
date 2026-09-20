"""Tests for canonical offset-array construction and validation."""

from array import array

import pytest

from archive_line_index.errors import InvalidIndexError
from archive_line_index.offsets import (
    MAX_OFFSET,
    line_count,
    line_range,
    make_offset_array,
    validate_offset_array,
)


@pytest.mark.parametrize(
    "values",
    [[0], [3], [0, 1], [3, 4], [0, 2, 5, 9]],
)
def test_valid_zero_one_and_multi_line_shapes(values: list[int]) -> None:
    offsets = make_offset_array(values)
    assert offsets.typecode == "Q"
    assert offsets.itemsize == 8
    assert list(validate_offset_array(offsets)) == values
    assert line_count(offsets) == len(values) - 1


def test_line_ranges_are_derived_from_adjacent_starts() -> None:
    offsets = make_offset_array([0, 2, 3, 7])
    assert line_range(offsets, 0) == (0, 2)
    assert line_range(offsets, 1) == (2, 3)
    assert line_range(offsets, 2) == (3, 7)


@pytest.mark.parametrize("value", [None, [0], (0,), b"\0" * 8])
def test_non_array_inputs_are_rejected(value) -> None:
    with pytest.raises(InvalidIndexError, match="must be an array"):
        validate_offset_array(value)


def test_wrong_array_type_code_is_rejected() -> None:
    with pytest.raises(InvalidIndexError, match="type code"):
        validate_offset_array(array("L", [0]))


def test_empty_array_is_rejected() -> None:
    with pytest.raises(InvalidIndexError, match="EOF sentinel"):
        validate_offset_array(array("Q"))


@pytest.mark.parametrize("values", [[1], [2, 3], [4], [MAX_OFFSET]])
def test_invalid_first_offset_is_rejected(values: list[int]) -> None:
    with pytest.raises(InvalidIndexError, match="first offset"):
        validate_offset_array(array("Q", values))


@pytest.mark.parametrize("values", [[0, 0], [3, 3], [0, 5, 4]])
def test_duplicate_and_descending_offsets_are_rejected(values: list[int]) -> None:
    with pytest.raises(InvalidIndexError, match="strictly increasing"):
        validate_offset_array(array("Q", values))


def test_offset_above_shared_signed_range_is_rejected() -> None:
    with pytest.raises(InvalidIndexError, match="SQLite range"):
        validate_offset_array(array("Q", [0, MAX_OFFSET + 1]))


@pytest.mark.parametrize("values", [[0, -1], [0, MAX_OFFSET + 1], [0, True], [0, 1.5]])
def test_constructor_rejects_unrepresentable_or_noninteger_values(values) -> None:
    with pytest.raises(InvalidIndexError):
        make_offset_array(values)


@pytest.mark.parametrize("line_number", [-1, 1])
def test_line_range_rejects_out_of_range_numbers(line_number: int) -> None:
    with pytest.raises(IndexError):
        line_range(make_offset_array([0, 4]), line_number)


@pytest.mark.parametrize("line_number", [True, 0.0, "0"])
def test_line_range_rejects_noninteger_numbers(line_number) -> None:
    with pytest.raises(TypeError):
        line_range(make_offset_array([0, 4]), line_number)
