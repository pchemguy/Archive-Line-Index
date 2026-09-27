"""Tests for the public API."""

from __future__ import annotations

import pytest

from archive_line_index.api import _validate_scan_options


def test_validate_scan_options_accepts_valid_inputs() -> None:
    _validate_scan_options(True, 1024)
    _validate_scan_options(False, 1)


@pytest.mark.parametrize("skip_utf8_bom", [0, 1, None, "True", 1.0])
def test_validate_scan_options_rejects_non_bool_skip_bom(skip_utf8_bom) -> None:
    with pytest.raises(TypeError, match="skip_utf8_bom must be a bool"):
        _validate_scan_options(skip_utf8_bom, 1024)


@pytest.mark.parametrize("buffer_size", [True, False, 1.5, "1024", None])
def test_validate_scan_options_rejects_non_int_buffer_size(buffer_size) -> None:
    with pytest.raises(TypeError, match="buffer_size must be an integer"):
        _validate_scan_options(True, buffer_size)


@pytest.mark.parametrize("buffer_size", [0, -1, -1024])
def test_validate_scan_options_rejects_nonpositive_buffer_size(buffer_size: int) -> None:
    with pytest.raises(ValueError, match="buffer_size must be positive"):
        _validate_scan_options(True, buffer_size)
