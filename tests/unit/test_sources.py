"""Filesystem normalization has no acquisition side effects."""

from pathlib import Path

import pytest

from archive_stream.sources import normalize_source


class BytesPath:
    def __fspath__(self) -> bytes:
        return b"payload"


@pytest.mark.parametrize("source", [b"data", 1, None, object(), BytesPath()])
def test_reject_nontext_paths(source: object) -> None:
    with pytest.raises(TypeError):
        normalize_source(source)  # type: ignore[arg-type]


def test_path_normalization_without_open(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert normalize_source(str(missing)) == missing
    assert normalize_source(missing) == missing
