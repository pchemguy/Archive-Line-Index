"""Tests for the public API."""

from __future__ import annotations

import pytest

from archive_line_index.api import (
    _validate_max_uncompressed_size,
    _validate_scan_options,
)


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


def test_validate_max_uncompressed_size_accepts_valid_inputs() -> None:
    _validate_max_uncompressed_size(None)
    _validate_max_uncompressed_size(0)
    _validate_max_uncompressed_size(1024)


@pytest.mark.parametrize("max_uncompressed_size", [True, False, 1.5, "1024"])
def test_validate_max_uncompressed_size_rejects_non_int(max_uncompressed_size) -> None:
    with pytest.raises(TypeError, match="max_uncompressed_size must be an integer or None"):
        _validate_max_uncompressed_size(max_uncompressed_size)


@pytest.mark.parametrize("max_uncompressed_size", [-1, -1024])
def test_validate_max_uncompressed_size_rejects_negative(max_uncompressed_size: int) -> None:
    with pytest.raises(ValueError, match="max_uncompressed_size must be non-negative"):
        _validate_max_uncompressed_size(max_uncompressed_size)

from unittest.mock import MagicMock, patch

from archive_line_index.api import (
    build_line_index,
    open_content_stream,
    read_raw_index,
    read_sqlite_index,
    scan_line_offsets,
    write_raw_index,
    write_sqlite_index,
)


@patch("archive_line_index.api.ContentStream")
@patch("archive_line_index.api.open_backend")
@patch("archive_line_index.api.detect_format")
@patch("archive_line_index.api.normalize_source_path")
def test_open_content_stream(
    mock_normalize, mock_detect, mock_open_backend, mock_content_stream
) -> None:
    mock_normalize.return_value = "normalized_path"
    mock_detect.return_value = "mock_format"
    mock_backend = MagicMock()
    mock_open_backend.return_value = mock_backend
    mock_stream_instance = MagicMock()
    mock_content_stream.return_value = mock_stream_instance

    result = open_content_stream("source_path", max_uncompressed_size=123)

    mock_normalize.assert_called_once_with("source_path")
    mock_detect.assert_called_once_with("normalized_path")
    mock_open_backend.assert_called_once_with("mock_format", "normalized_path")
    mock_content_stream.assert_called_once_with(mock_backend, max_uncompressed_size=123)
    assert result is mock_stream_instance


@patch("archive_line_index.api.scan_offsets")
def test_scan_line_offsets(mock_scan_offsets) -> None:
    mock_stream = MagicMock()
    mock_array = MagicMock()
    mock_scan_offsets.return_value = mock_array

    result = scan_line_offsets(mock_stream, skip_utf8_bom=False, buffer_size=512)

    mock_scan_offsets.assert_called_once_with(
        mock_stream, skip_utf8_bom=False, buffer_size=512
    )
    assert result is mock_array


@patch("archive_line_index.api.scan_line_offsets")
@patch("archive_line_index.api.open_content_stream")
def test_build_line_index(mock_open_content_stream, mock_scan_line_offsets) -> None:
    mock_stream_instance = MagicMock()
    # Support context manager
    mock_stream_instance.__enter__.return_value = mock_stream_instance
    mock_open_content_stream.return_value = mock_stream_instance
    mock_array = MagicMock()
    mock_scan_line_offsets.return_value = mock_array

    result = build_line_index(
        "source_path", skip_utf8_bom=False, buffer_size=512, max_uncompressed_size=123
    )

    mock_open_content_stream.assert_called_once_with(
        "source_path", max_uncompressed_size=123
    )
    mock_stream_instance.__enter__.assert_called_once()
    mock_scan_line_offsets.assert_called_once_with(
        mock_stream_instance, skip_utf8_bom=False, buffer_size=512
    )
    mock_stream_instance.__exit__.assert_called_once()
    assert result is mock_array


@patch("archive_line_index.api._write_sqlite_index")
def test_write_sqlite_index(mock_write_sqlite) -> None:
    mock_array = MagicMock()
    write_sqlite_index(mock_array, "dest.sqlite", overwrite=True)
    mock_write_sqlite.assert_called_once_with(mock_array, "dest.sqlite", overwrite=True)


@patch("archive_line_index.api._read_sqlite_index")
def test_read_sqlite_index(mock_read_sqlite) -> None:
    mock_array = MagicMock()
    mock_read_sqlite.return_value = mock_array
    result = read_sqlite_index("source.sqlite")
    mock_read_sqlite.assert_called_once_with("source.sqlite")
    assert result is mock_array


@patch("archive_line_index.api._write_raw_index")
def test_write_raw_index(mock_write_raw) -> None:
    mock_array = MagicMock()
    write_raw_index(mock_array, "dest.raw", overwrite=True)
    mock_write_raw.assert_called_once_with(mock_array, "dest.raw", overwrite=True)


@patch("archive_line_index.api._read_raw_index")
def test_read_raw_index(mock_read_raw) -> None:
    mock_array = MagicMock()
    mock_read_raw.return_value = mock_array
    result = read_raw_index("source.raw")
    mock_read_raw.assert_called_once_with("source.raw")
    assert result is mock_array
