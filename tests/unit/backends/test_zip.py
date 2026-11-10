"""ZIP metadata validation uses real archives and rejects unsafe member kinds."""

import stat
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_stream.errors import (
    ArchiveStructureError,
    InvalidArchiveError,
    UnsupportedFormatError,
)


def make_zip(path: Path, entries: list[tuple[str, bytes, int]]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data, mode in entries:
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = mode << 16
            archive.writestr(info, data)
    return path


@pytest.mark.parametrize("payload", [b"", b"a\n\xff"])
def test_sole_nested_regular_member(tmp_path: Path, payload: bytes) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(
        tmp_path / "a.zip",
        [("folder/", b"", stat.S_IFDIR), ("../folder/data", payload, stat.S_IFREG)],
    )
    reader = open_zip_backend(p)
    assert reader.declared_size == len(payload)
    reader.close()
    reader.close()
    assert sorted(x.name for x in tmp_path.iterdir()) == ["a.zip"]
    p.unlink()


@pytest.mark.parametrize(
    "names", [[], ["folder/"], ["a", "b"], ["a", "__MACOSX/metadata"]]
)
def test_invalid_member_counts(tmp_path: Path, names: list[str]) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(
        tmp_path / "a.zip",
        [(n, b"", stat.S_IFDIR if n.endswith("/") else stat.S_IFREG) for n in names],
    )
    with pytest.raises(ArchiveStructureError):
        open_zip_backend(p)
    p.unlink()


@pytest.mark.parametrize(
    "kind", [stat.S_IFLNK, stat.S_IFIFO, stat.S_IFSOCK, stat.S_IFCHR, stat.S_IFBLK]
)
def test_special_metadata_is_not_a_regular_file(tmp_path: Path, kind: int) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("special", b"target", kind)])
    with pytest.raises(ArchiveStructureError):
        open_zip_backend(p)
    p.unlink()


def test_detected_encryption_is_unsupported(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("a", b"secret", stat.S_IFREG)])
    data = bytearray(p.read_bytes())
    # Set the encryption flag in both actual ZIP headers; no password is supplied.
    for signature, offset in [(b"PK\x03\x04", 6), (b"PK\x01\x02", 8)]:
        data[data.index(signature) + offset] |= 1
    p.write_bytes(data)
    with pytest.raises(UnsupportedFormatError):
        open_zip_backend(p)
    p.unlink()


def test_invalid_open_preserves_cause_and_releases_source(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = tmp_path / "bad.zip"
    p.write_bytes(b"not ZIP")
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        with pytest.raises(InvalidArchiveError) as error:
            open_zip_backend(p)
    assert isinstance(error.value.__cause__, zipfile.BadZipFile)
    assert handle.closed
    with pytest.raises(FileNotFoundError):
        open_zip_backend(tmp_path / "missing")


@pytest.mark.parametrize(
    "compression",
    [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA],
)
def test_bounded_delivery_and_terminal_validation(
    tmp_path: Path, compression: int
) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = tmp_path / "data.zip"
    payload = b"\0a\n\xff" * 4000
    with zipfile.ZipFile(p, "w", compression=compression) as archive:
        archive.writestr("data", payload)
    reader = open_zip_backend(p)
    chunks = []
    while block := reader.read(13):
        assert len(block) <= 13
        chunks.append(block)
    assert b"".join(chunks) == payload
    assert reader.completed
    assert reader.read(1) == b""
    reader.close()
    p.unlink()


def test_crc_failure_is_extraction_error_not_eof(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend
    from archive_stream.errors import ExtractionError
    from archive_stream.stream import make_content_stream

    p = make_zip(tmp_path / "bad.zip", [("data", b"unchanged\n", stat.S_IFREG)])
    raw = bytearray(p.read_bytes())
    raw[30 + len("data")] ^= 1
    p.write_bytes(raw)
    reader = open_zip_backend(p)
    stream = make_content_stream(reader, max_uncompressed_size=None)
    with pytest.raises(ExtractionError) as first:
        stream.read()
    assert isinstance(first.value.__cause__, zipfile.BadZipFile)
    assert not reader.completed
    with pytest.raises(ExtractionError) as second:
        stream.read(1)
    assert second.value is first.value
    stream.close()
    p.unlink()


def test_open_member_codec_failure_releases_all_handles(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("data", b"x", stat.S_IFREG)])
    handle = p.open("rb")
    with (
        patch.object(Path, "open", return_value=handle),
        patch.object(zipfile.ZipFile, "open", side_effect=NotImplementedError("codec")),
    ):
        with pytest.raises(UnsupportedFormatError) as error:
            open_zip_backend(p)
    assert isinstance(error.value.__cause__, NotImplementedError)
    assert handle.closed


def test_declared_limit_and_invalid_read_sizes(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend
    from archive_stream.errors import SizeLimitExceededError
    from archive_stream.stream import make_content_stream

    p = make_zip(tmp_path / "a.zip", [("data", b"1234", stat.S_IFREG)])
    reader = open_zip_backend(p)
    with pytest.raises(SizeLimitExceededError):
        make_content_stream(reader, max_uncompressed_size=3)
    reader = open_zip_backend(p)
    try:
        for size, error in [(0, ValueError), (-1, ValueError), (True, TypeError)]:
            with pytest.raises(error):
                reader.read(size)
        assert reader.read(1) == b"1"
    finally:
        reader.close()


def test_delivery_filesystem_failure_retains_original_type(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("data", b"data" * 10000, stat.S_IFREG)])
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        reader = open_zip_backend(p)
    failure = PermissionError("source device")
    with patch.object(handle, "read", side_effect=failure):
        with pytest.raises(PermissionError) as error:
            reader.read(10000)
    assert error.value is failure
    assert not reader.completed
    reader.close()
    assert handle.closed


def test_close_attempts_all_resources_and_can_retry(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("data", b"x", stat.S_IFREG)])
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        reader = open_zip_backend(p)
    with patch.object(zipfile.ZipExtFile, "close", side_effect=OSError("member close")):
        with pytest.raises(OSError, match="member close"):
            reader.close()
    assert handle.closed
    reader.close()
    reader.close()


@pytest.mark.parametrize(
    "compression", [zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA]
)
def test_corrupt_compressed_member_cannot_complete(
    tmp_path: Path, compression: int
) -> None:
    from archive_stream.backends.zip import open_zip_backend
    from archive_stream.errors import ExtractionError

    p = tmp_path / "bad.zip"
    with zipfile.ZipFile(p, "w", compression=compression) as archive:
        archive.writestr("data", b"a\n" * 20000)
    raw = bytearray(p.read_bytes())
    start = 30 + len("data")
    raw[start + 3] ^= 0xFF
    p.write_bytes(raw)
    reader = open_zip_backend(p)
    try:
        with pytest.raises(ExtractionError):
            while reader.read(128):
                pass
        assert not reader.completed
    finally:
        reader.close()


def test_delivery_position_io_failure_is_not_a_codec_error(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("data", b"x" * 10000, stat.S_IFREG)])
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        reader = open_zip_backend(p)
    failure = OSError("source position")
    try:
        with patch.object(handle, "tell", side_effect=failure):
            with pytest.raises(OSError) as error:
                reader.read(1)
        assert error.value is failure
    finally:
        reader.close()


@pytest.mark.parametrize(
    "compression",
    [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA],
)
@pytest.mark.parametrize("declared", [2, 100], ids=["underdeclared", "overdeclared"])
def test_mismatched_size_cannot_complete(
    tmp_path: Path, compression: int, declared: int
) -> None:
    from tests.helpers.archives import make_zip_with_size_metadata

    from archive_stream.backends.zip import open_zip_backend
    from archive_stream.errors import ExtractionError

    target = make_zip_with_size_metadata(
        tmp_path / "bad.zip", b"hello\n", declared, compression=compression
    )
    reader = open_zip_backend(target)
    try:
        with pytest.raises(ExtractionError):
            while reader.read(2):
                pass
        assert not reader.completed
    finally:
        reader.close()


def test_dependency_excess_bytes_are_rejected_before_delivery(tmp_path: Path) -> None:
    from archive_stream.backends.zip import open_zip_backend
    from archive_stream.errors import ExtractionError

    target = make_zip(tmp_path / "data.zip", [("data", b"x", stat.S_IFREG)])
    reader = open_zip_backend(target)
    try:
        with patch.object(zipfile.ZipExtFile, "read", return_value=b"excess"):
            with pytest.raises(ExtractionError):
                reader.read(6)
        assert not reader.completed
    finally:
        reader.close()
