"""Real in-process paired CLI workflows and partial-publication diagnostics."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_stream import cli, read_raw_index, read_sqlite_index, scan_line_offsets


@pytest.mark.parametrize("payload", [b"", b"\xef\xbb\xbf", b"a\nb", b"a\r\n\nlast"])
def test_real_imported_cli_pair(
    tmp_path: Path, payload: bytes, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(payload)
    with patch.object(cli, "build_line_index", wraps=cli.build_line_index) as build:
        assert cli.main([str(source)]) == 0
    build.assert_called_once()
    expected = scan_line_offsets(io.BytesIO(payload))
    assert (
        read_sqlite_index(tmp_path / "payload.sqlite3")
        == read_raw_index(tmp_path / "payload.u64")
        == expected
    )
    out, err = capsys.readouterr()
    assert not err and str(len(expected) - 1) in out
    assert source.read_bytes() == payload


def test_raw_failure_retains_sqlite_and_reports_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"a\nb")
    with patch.object(cli, "write_raw_index", side_effect=OSError("raw failed")):
        assert cli.main([str(source)]) == 1
    assert read_sqlite_index(tmp_path / "payload.sqlite3").tolist() == [0, 2, 3]
    assert not (tmp_path / "payload.u64").exists()
    out, err = capsys.readouterr()
    assert not out and "raw failed" in err and str(tmp_path / "payload.sqlite3") in err


def test_postpublication_cleanup_note_and_no_later_writer(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"abc")
    real_unlink = Path.unlink

    def fail_temporary(path: Path, missing_ok: bool = False) -> None:
        if path.suffix == ".tmp":
            raise PermissionError("cleanup fault")
        real_unlink(path, missing_ok=missing_ok)

    with (
        patch.object(Path, "unlink", fail_temporary),
        patch.object(
            cli, "write_raw_index", side_effect=AssertionError("later writer")
        ),
    ):
        assert cli.main([str(source)]) == 1
    assert read_sqlite_index(tmp_path / "payload.sqlite3").tolist() == [0, 3]
    out, err = capsys.readouterr()
    assert (
        not out
        and "Publication already succeeded" in err
        and str(tmp_path / "payload.sqlite3") in err
    )
    for temporary in tmp_path.glob(".*.tmp"):
        temporary.unlink()


def test_no_parent_creation_or_outputs_after_source_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"abc")
    assert cli.main([str(source), "--output", str(tmp_path / "missing" / "out")]) == 1
    assert not (tmp_path / "missing").exists()
    archive = tmp_path / "claimed.zip"
    archive.write_bytes(b"invalid")
    assert cli.main([str(archive)]) == 1
    assert (
        not (tmp_path / "claimed.sqlite3").exists()
        and not (tmp_path / "claimed.u64").exists()
    )
    out, err = capsys.readouterr()
    assert not out and err


def test_raw_postpublication_cleanup_reports_both_completed_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"abc")
    real_unlink = Path.unlink

    def fail_raw_temporary(path: Path, missing_ok: bool = False) -> None:
        if path.name.startswith(".payload.u64.") and path.suffix == ".tmp":
            raise PermissionError("raw cleanup fault")
        real_unlink(path, missing_ok=missing_ok)

    with patch.object(Path, "unlink", fail_raw_temporary):
        assert cli.main([str(source)]) == 1
    assert read_sqlite_index(tmp_path / "payload.sqlite3") == read_raw_index(
        tmp_path / "payload.u64"
    )
    out, err = capsys.readouterr()
    assert (
        not out
        and str(tmp_path / "payload.sqlite3") in err
        and str(tmp_path / "payload.u64") in err
    )
    assert "Publication already succeeded" in err
    for temporary in tmp_path.glob(".*.tmp"):
        temporary.unlink()


def test_interrupt_inside_raw_writer_cleans_owned_temporary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"abc")
    with patch(
        "archive_stream.persistence.raw._write_all", side_effect=KeyboardInterrupt
    ):
        assert cli.main([str(source)]) == 130
    assert read_sqlite_index(tmp_path / "payload.sqlite3").tolist() == [0, 3]
    assert not (tmp_path / "payload.u64").exists()
    assert {p.name for p in tmp_path.iterdir()} == {"payload.txt", "payload.sqlite3"}
    out, err = capsys.readouterr()
    assert not out and "Interrupted" in err and str(tmp_path / "payload.sqlite3") in err
