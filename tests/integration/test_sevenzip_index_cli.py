"""7z indexing and paired publication require validated extraction completion."""

from pathlib import Path
from unittest.mock import patch

import py7zr
import pytest
from tests.helpers.sevenzip import make_7z
from tests.integration.test_sevenzip_stream import owned_threads

from archive_line_index import (
    ExtractionError,
    build_line_index,
    read_raw_index,
    read_sqlite_index,
)
from archive_line_index.cli import main


@pytest.mark.parametrize(
    "payload,expected",
    [
        (b"", [0]),
        (b"\xef\xbb\xbf", [3]),
        (b"a\nb", [0, 2, 3]),
        (b"\r\n\nlast", [0, 2, 3, 7]),
        (b"a\n", [0, 2]),
        (b"\0\xff\nx", [0, 3, 4]),
    ],
)
@pytest.mark.parametrize("buffer_size", [1, 2, 7])
def test_actual_7z_index_and_pair_equivalence(
    tmp_path: Path, payload: bytes, expected: list[int], buffer_size: int
) -> None:
    target = make_7z(tmp_path / "payload.7z", [("nested/data", payload)])
    plain = tmp_path / "plain"
    plain.write_bytes(payload)
    before = owned_threads()
    assert build_line_index(target, buffer_size=buffer_size).tolist() == expected
    assert build_line_index(target) == build_line_index(plain)
    assert main([str(target)]) == 0
    assert read_sqlite_index(tmp_path / "payload.sqlite3").tolist() == expected
    assert read_raw_index(tmp_path / "payload.u64").tolist() == expected
    assert owned_threads() == before


def test_late_7z_crc_failure_never_invokes_output_writers(tmp_path: Path) -> None:
    target = make_7z(
        tmp_path / "bad.7z", [("data", b"a\nb\n")], filters=[{"id": py7zr.FILTER_COPY}]
    )
    raw = bytearray(target.read_bytes())
    raw[35] ^= 1
    target.write_bytes(raw)
    before = owned_threads()
    with pytest.raises(ExtractionError):
        build_line_index(target, buffer_size=1)
    with (
        patch(
            "archive_line_index.cli.write_sqlite_index",
            side_effect=AssertionError("premature SQLite"),
        ),
        patch(
            "archive_line_index.cli.write_raw_index",
            side_effect=AssertionError("premature raw"),
        ),
    ):
        assert main([str(target)]) == 1
    assert not target.with_suffix(".sqlite3").exists()
    assert not target.with_suffix(".u64").exists()
    assert owned_threads() == before


def test_7z_raw_failure_retains_sqlite_after_worker_is_joined(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import archive_line_index.cli as cli

    target = make_7z(tmp_path / "payload.7z", [("data", b"a\nb")])
    before = owned_threads()
    original = cli.write_sqlite_index

    def write_sqlite(*args: object, **kwargs: object) -> None:
        assert owned_threads() == before
        original(*args, **kwargs)

    with (
        patch.object(cli, "write_sqlite_index", write_sqlite),
        patch(
            "archive_line_index.persistence.raw._write_all",
            side_effect=OSError("raw failure"),
        ),
    ):
        assert main([str(target)]) == 1
    captured = capsys.readouterr()
    assert not captured.out and "Already published" in captured.err
    assert read_sqlite_index(target.with_suffix(".sqlite3")).tolist() == [0, 2, 3]
    assert not target.with_suffix(".u64").exists()
    assert owned_threads() == before
