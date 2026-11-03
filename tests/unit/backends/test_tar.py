"""Sequential TAR adapters own handles and expose only a regular payload."""

import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.helpers.archives import make_tar

from archive_line_index.errors import ArchiveStructureError, InvalidArchiveError


@pytest.mark.parametrize("payload", [b"", b"a\n\xff" * 10000])
@pytest.mark.parametrize(
    "format", [tarfile.USTAR_FORMAT, tarfile.PAX_FORMAT, tarfile.GNU_FORMAT]
)
def test_plain_tar_nested_empty_and_bounded_reads(
    tmp_path: Path, payload: bytes, format: int
) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "a.tar",
        [
            ("folder", b"", tarfile.DIRTYPE),
            ("../folder/data", payload, tarfile.REGTYPE),
        ],
        format=format,
    )
    reader = open_tar_backend(p)
    assert reader.declared_size == len(payload)
    blocks = []
    while data := reader.read(7):
        assert len(data) <= 7
        blocks.append(data)
    assert b"".join(blocks) == payload
    assert reader.completed
    reader.close()
    reader.close()
    assert sorted(x.name for x in tmp_path.iterdir()) == ["a.tar"]
    p.unlink()


@pytest.mark.parametrize(
    "kind",
    [
        tarfile.SYMTYPE,
        tarfile.LNKTYPE,
        tarfile.CHRTYPE,
        tarfile.BLKTYPE,
        tarfile.FIFOTYPE,
    ],
)
def test_special_entries_before_payload_are_rejected(
    tmp_path: Path, kind: bytes
) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "a.tar", [("special", b"", kind), ("data", b"x", tarfile.REGTYPE)]
    )
    with pytest.raises(ArchiveStructureError):
        open_tar_backend(p)
    p.unlink()


def test_no_regular_file_is_rejected(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(tmp_path / "a.tar", [("folder", b"", tarfile.DIRTYPE)])
    with pytest.raises(ArchiveStructureError):
        open_tar_backend(p)


def test_tar_early_close_and_opening_failure_own_source(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(tmp_path / "a.tar", [("data", b"large" * 10000, tarfile.REGTYPE)])
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        reader = open_tar_backend(p)
    assert reader.read(1) == b"l"
    reader.close()
    assert handle.closed
    p.write_bytes(b"invalid")
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        with pytest.raises(InvalidArchiveError) as error:
            open_tar_backend(p)
    assert isinstance(error.value.__cause__, tarfile.ReadError)
    assert handle.closed
    with pytest.raises(FileNotFoundError):
        open_tar_backend(tmp_path / "missing")


def test_tar_extension_headers_are_not_exposed_files(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "a.tar", [("nested/" + "x" * 200, b"data", tarfile.REGTYPE)]
    )
    reader = open_tar_backend(p)
    assert reader.read(9) == b"data"
    assert reader.read(1) == b""
    reader.close()
