"""Public TAR selection and paired outputs preserve payload coordinates."""

import gzip
import tarfile
from pathlib import Path

import pytest
from tests.helpers.archives import make_tar

from archive_stream import (
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
    build_line_index,
    open_content_stream,
    read_raw_index,
    read_sqlite_index,
)
from archive_stream.cli import main

VARIANTS = [
    (".tar", "w"),
    (".tar.gz", "w:gz"),
    (".tgz", "w:gz"),
    (".tar.bz2", "w:bz2"),
    (".tbz", "w:bz2"),
    (".tbz2", "w:bz2"),
    (".tar.xz", "w:xz"),
    (".txz", "w:xz"),
    (".unknown", "w:gz"),
    (".zip", "w:xz"),
]


@pytest.mark.parametrize("suffix,mode", VARIANTS)
@pytest.mark.parametrize("buffer_size", [1, 7])
def test_all_tar_forms_index_and_publish_matching_pairs(
    tmp_path: Path, suffix: str, mode: str, buffer_size: int
) -> None:
    payload = b"\xef\xbb\xbfalpha\r\n\nomega"
    target = make_tar(
        tmp_path / ("source" + suffix),
        [("nested/data", payload, tarfile.REGTYPE)],
        mode=mode,
    )
    plain = tmp_path / "plain"
    plain.write_bytes(payload)
    assert build_line_index(target, buffer_size=buffer_size).tolist() == [3, 10, 11, 16]
    assert build_line_index(target) == build_line_index(plain)
    with open_content_stream(target, max_uncompressed_size=len(payload)) as stream:
        blocks = []
        while block := stream.read(3):
            blocks.append(block)
        assert b"".join(blocks) == payload
    with pytest.raises(SizeLimitExceededError):
        build_line_index(target, max_uncompressed_size=len(payload) - 1)
    assert main([str(target)]) == 0
    stem = target.with_suffix("")
    assert read_sqlite_index(str(stem) + ".sqlite3").tolist() == [3, 10, 11, 16]
    assert read_raw_index(str(stem) + ".u64").tolist() == [3, 10, 11, 16]


@pytest.mark.parametrize("mode", ["w", "w:gz", "w:bz2", "w:xz"])
def test_late_extra_member_cannot_publish_outputs(
    tmp_path: Path, mode: str, capsys: pytest.CaptureFixture[str]
) -> None:
    target = make_tar(
        tmp_path / "bad.tar",
        [
            ("data", b"a\nb", tarfile.REGTYPE),
            ("__MACOSX/metadata", b"extra", tarfile.REGTYPE),
        ],
        mode=mode,
    )
    with pytest.raises(ArchiveStructureError):
        build_line_index(target, buffer_size=1)
    assert main([str(target)]) == 1
    assert not capsys.readouterr().out
    assert not target.with_suffix(".sqlite3").exists()
    assert not target.with_suffix(".u64").exists()


def test_tar_candidates_do_not_fall_back_to_plain(tmp_path: Path) -> None:
    target = tmp_path / "bad.tar"
    target.write_bytes(b"plain\n")
    with pytest.raises(InvalidArchiveError):
        build_line_index(target)
    target = tmp_path / "non-tar.unknown"
    target.write_bytes(gzip.compress(b"not tar"))
    with pytest.raises(InvalidArchiveError):
        build_line_index(target)


def test_late_gzip_crc_error_cannot_complete_or_publish(tmp_path: Path) -> None:
    target = make_tar(tmp_path / "bad.tgz", [("data", b"a\nb", tarfile.REGTYPE)])
    raw = bytearray(gzip.compress(target.read_bytes() + b"\0" * (128 * 1024)))
    raw[-8] ^= 1
    target.write_bytes(raw)
    with pytest.raises(ExtractionError):
        build_line_index(target, buffer_size=1)
    assert main([str(target)]) == 1
    assert not target.with_suffix(".sqlite3").exists()
    assert not target.with_suffix(".u64").exists()
