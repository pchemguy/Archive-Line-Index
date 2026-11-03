"""Independent public persistence preserves exactly the canonical offset model."""

import io
from array import array
from pathlib import Path

import pytest

import archive_line_index as ali


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\xef\xbb\xbf",
        b"abc",
        b"abc\r\n",
        b"\n\n",
        b"a\n\nb",
        b"\xef\xbb\xbfabc\n",
    ],
)
def test_public_cross_format_equivalence_without_payload_path(
    tmp_path: Path, payload: bytes
) -> None:
    offsets = ali.scan_line_offsets(io.BytesIO(payload), buffer_size=1)
    original = offsets.tobytes()
    sqlite = tmp_path / "index.sqlite3"
    raw = tmp_path / "index.u64"
    assert ali.write_sqlite_index(offsets, sqlite) is None
    assert ali.write_raw_index(offsets, raw) is None
    assert ali.read_sqlite_index(sqlite) == ali.read_raw_index(raw) == offsets
    assert offsets.tobytes() == original
    with pytest.raises(FileExistsError):
        ali.write_sqlite_index(offsets, sqlite)
    with pytest.raises(FileExistsError):
        ali.write_raw_index(offsets, raw)
    ali.write_sqlite_index(array("Q", [3]), sqlite, overwrite=True)
    assert ali.read_sqlite_index(sqlite).tolist() == [3]
    assert ali.read_raw_index(raw) == offsets
