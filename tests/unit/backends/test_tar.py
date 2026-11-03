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


@pytest.mark.parametrize(
    "kind",
    [
        tarfile.REGTYPE,
        tarfile.SYMTYPE,
        tarfile.LNKTYPE,
        tarfile.CHRTYPE,
        tarfile.FIFOTYPE,
    ],
)
def test_late_member_fails_after_payload_before_eof(
    tmp_path: Path, kind: bytes
) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "a.tar",
        [("data", b"payload", tarfile.REGTYPE), ("late", b"extra", kind)],
    )
    reader = open_tar_backend(p)
    try:
        assert reader.read(7) == b"payload"
        assert not reader.completed
        with pytest.raises(ArchiveStructureError):
            reader.read(1)
        assert not reader.completed
    finally:
        reader.close()


@pytest.mark.parametrize(
    "failure", ["bad-header", "no-end", "half-end", "nonzero-tail", "partial-payload"]
)
def test_malformed_trailing_structure_cannot_complete(
    tmp_path: Path, failure: str
) -> None:
    from archive_line_index.backends.tar import open_tar_backend
    from archive_line_index.errors import ExtractionError
    from archive_line_index.scanner import scan_line_offsets
    from archive_line_index.stream import make_content_stream

    p = make_tar(tmp_path / "a.tar", [("data", b"x\n" * 300, tarfile.REGTYPE)])
    raw = p.read_bytes()
    end = 512 + 1024
    if failure == "bad-header":
        raw = raw[:end] + b"!" * 512 + raw[end + 512 :]
    elif failure == "no-end":
        raw = raw[:end]
    elif failure == "half-end":
        raw = raw[: end + 512]
    elif failure == "nonzero-tail":
        raw += b"garbage"
    else:
        raw = raw[:600]
    p.write_bytes(raw)
    stream = make_content_stream(open_tar_backend(p), max_uncompressed_size=None)
    try:
        with pytest.raises(ExtractionError):
            scan_line_offsets(stream, buffer_size=5)
    finally:
        stream.close()


def test_trailing_directories_and_repeated_eof(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "a.tar",
        [("data", b"x", tarfile.REGTYPE), ("later", b"", tarfile.DIRTYPE)],
    )
    reader = open_tar_backend(p)
    try:
        assert reader.read(1) == b"x"
        assert reader.read(1) == b""
        assert reader.completed
        assert reader.read(1) == b""
    finally:
        reader.close()
