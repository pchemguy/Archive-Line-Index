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


@pytest.mark.parametrize("mode", ["w:gz", "w:bz2", "w:xz"])
def test_required_compressed_tar_exact_delivery(tmp_path: Path, mode: str) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    payload = b"\0a\n\xff" * 4000
    p = make_tar(
        tmp_path / "unconventional",
        [("nested/data", payload, tarfile.REGTYPE)],
        mode=mode,
    )
    reader = open_tar_backend(p)
    try:
        assert reader.declared_size == len(payload)
        blocks = []
        while block := reader.read(11):
            assert len(block) <= 11
            blocks.append(block)
        assert b"".join(blocks) == payload
        assert reader.completed
    finally:
        reader.close()


@pytest.mark.parametrize("codec", ["gzip", "bz2", "lzma"])
def test_compressed_non_tar_and_bad_trailer_cannot_succeed(
    tmp_path: Path, codec: str
) -> None:
    import importlib

    from archive_line_index.backends.tar import open_tar_backend
    from archive_line_index.errors import ExtractionError
    from archive_line_index.scanner import scan_line_offsets
    from archive_line_index.stream import make_content_stream

    compressor = importlib.import_module(codec).compress
    p = tmp_path / "compressed"
    p.write_bytes(compressor(b"plain bytes, not tar"))
    with pytest.raises(InvalidArchiveError):
        open_tar_backend(p)
    make_tar(p, [("data", b"payload\n", tarfile.REGTYPE)])
    raw = compressor(p.read_bytes() + b"\0" * (128 * 1024))
    damaged = bytearray(raw)
    damaged[-5] ^= 0xFF
    p.write_bytes(damaged)
    # Codecs may detect damage while opening or while completing delivery.
    with pytest.raises((InvalidArchiveError, ExtractionError)) as error:
        stream = make_content_stream(open_tar_backend(p), max_uncompressed_size=None)
        try:
            scan_line_offsets(stream, buffer_size=3)
        finally:
            stream.close()
    assert error.value.__cause__ is not None
    p.write_bytes(raw[:-8])
    with pytest.raises((InvalidArchiveError, ExtractionError)):
        reader = open_tar_backend(p)
        try:
            while reader.read(31):
                pass
        finally:
            reader.close()


def test_missing_selected_codec_is_unsupported(tmp_path: Path) -> None:
    import sys

    from archive_line_index.backends.tar import open_tar_backend
    from archive_line_index.errors import UnsupportedFormatError

    p = make_tar(tmp_path / "a.tar.xz", [("data", b"x", tarfile.REGTYPE)], mode="w:xz")
    handle = p.open("rb")
    with (
        patch.object(Path, "open", return_value=handle),
        patch.dict(sys.modules, {"lzma": None}),
    ):
        with pytest.raises(UnsupportedFormatError) as error:
            open_tar_backend(p)
    assert isinstance(error.value.__cause__, ImportError)
    assert handle.closed


@pytest.mark.parametrize("mode", ["w", "w:gz", "w:bz2", "w:xz"])
def test_tar_source_io_failure_remains_ordinary(tmp_path: Path, mode: str) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    # Exercise source failures during bounded delivery or the mandatory terminal drain.
    payload = bytes(range(256)) * 1024
    p = make_tar(tmp_path / "source", [("data", payload, tarfile.REGTYPE)], mode=mode)
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        reader = open_tar_backend(p)
    failure = PermissionError("source read")
    try:
        with patch.object(handle, "read", side_effect=failure):
            with pytest.raises(PermissionError) as error:
                while reader.read(1024):
                    pass
        assert error.value is failure
        assert not reader.completed
    finally:
        reader.close()
    assert handle.closed


def test_gzip_footer_is_validated_after_payload_delivery(tmp_path: Path) -> None:
    import gzip

    from archive_line_index.backends.tar import open_tar_backend
    from archive_line_index.errors import ExtractionError

    p = make_tar(tmp_path / "a", [("data", b"payload\n", tarfile.REGTYPE)])
    raw = bytearray(gzip.compress(p.read_bytes() + b"\0" * (128 * 1024)))
    raw[-8] ^= 1
    p.write_bytes(raw)
    reader = open_tar_backend(p)
    try:
        assert reader.read(8) == b"payload\n"
        assert not reader.completed
        with pytest.raises(ExtractionError) as error:
            reader.read(1)
        assert isinstance(error.value.__cause__, gzip.BadGzipFile)
        assert not reader.completed
    finally:
        reader.close()


def test_negative_declared_tar_size_is_invalid_at_open(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    info = tarfile.TarInfo("data")
    info.size = -1
    p = tmp_path / "bad.tar"
    p.write_bytes(info.tobuf(format=tarfile.GNU_FORMAT) + b"\0" * 1024)
    with pytest.raises(InvalidArchiveError):
        reader = open_tar_backend(p)
        reader.close()


def test_tar_close_attempts_all_handles_and_retries(tmp_path: Path) -> None:
    from archive_line_index.backends.tar import open_tar_backend

    p = make_tar(
        tmp_path / "data", [("data", b"payload", tarfile.REGTYPE)], mode="w:gz"
    )
    source = p.open("rb")
    with patch.object(Path, "open", return_value=source):
        reader = open_tar_backend(p)
    with patch.object(
        tarfile.ExFileObject, "close", side_effect=OSError("member cleanup")
    ):
        with pytest.raises(OSError, match="member cleanup"):
            reader.close()
    assert source.closed
    reader.close()
    reader.close()
