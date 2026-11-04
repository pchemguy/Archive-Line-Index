"""Delivered adapter selection preserves ordinary source-opening failures."""

from pathlib import Path

import pytest

from archive_line_index.backends.registry import open_backend
from archive_line_index.formats import FormatCandidate, FormatKind


@pytest.mark.parametrize("kind", list(FormatKind))
def test_missing_source_retains_filesystem_category(
    tmp_path: Path, kind: FormatKind
) -> None:
    with pytest.raises(FileNotFoundError):
        open_backend(tmp_path / "missing", FormatCandidate(kind, None, kind))


def test_plain_candidate_opens_original_bytes(tmp_path: Path) -> None:
    p = tmp_path / "p"
    p.write_bytes(b"data")
    r = open_backend(p, FormatCandidate(FormatKind.PLAIN, None, None))
    try:
        assert r.read(99) == b"data"
    finally:
        r.close()
