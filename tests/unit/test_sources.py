"""Tests for path-only source normalization."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from archive_line_index.sources import normalize_source_path


@pytest.mark.parametrize("as_path", [False, True])
def test_string_and_pathlike_sources_normalize_to_string(
    tmp_path: Path, as_path: bool
) -> None:
    path = tmp_path / "payload.bin"
    source = path if as_path else str(path)

    assert normalize_source_path(source) == str(path)


def test_normalization_does_not_open_or_require_existing_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.bin"
    assert normalize_source_path(path) == str(path)


def test_bytes_pathlike_is_rejected() -> None:
    class BytesPath:
        def __fspath__(self) -> bytes:
            return b"payload.bin"

    with pytest.raises(TypeError, match="resolve to str"):
        normalize_source_path(BytesPath())


@pytest.mark.parametrize("source", [io.BytesIO(b"data"), object(), 7])
def test_non_path_sources_are_rejected(source) -> None:
    with pytest.raises(TypeError, match="filesystem path"):
        normalize_source_path(source)
