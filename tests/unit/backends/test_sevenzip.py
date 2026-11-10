"""Real py7zr archives exercise metadata, callback streaming and ownership."""

from pathlib import Path
from unittest.mock import patch

import py7zr
import pytest
from tests.helpers.sevenzip import make_7z

from archive_stream.errors import (
    ArchiveStructureError,
    InvalidArchiveError,
    UnsupportedFormatError,
)


@pytest.mark.parametrize(
    "payload",
    [b"", b"\xef\xbb\xbfalpha\r\n\nomega", b"\0\xff" * 10000],
    ids=["empty", "bom-text", "binary-20k"],
)
def test_real_7z_nested_payload_without_filesystem_extraction(
    tmp_path: Path, payload: bytes
) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(tmp_path / "source.7z", [("nested/data", payload)])
    with patch.object(Path, "mkdir", side_effect=AssertionError("member extraction")):
        reader = open_7z_backend(p)
        try:
            assert reader.declared_size == len(payload)
            blocks = []
            while data := reader.read(7):
                assert len(data) <= 7
                blocks.append(data)
            assert b"".join(blocks) == payload
            assert reader.completed
        finally:
            reader.close()
    reader.close()
    assert sorted(x.name for x in tmp_path.iterdir()) == ["source.7z"]
    p.unlink()


@pytest.mark.parametrize(
    "entries",
    [[], [("a", b"x"), ("b", b"y")], [("a", b"x"), ("__MACOSX/metadata", b"y")]],
)
def test_7z_member_counts_are_validated_before_extraction(
    tmp_path: Path, entries: list[tuple[str, bytes]]
) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(tmp_path / "source.7z", entries)
    with pytest.raises(ArchiveStructureError):
        open_7z_backend(p)
    p.unlink()


@pytest.mark.parametrize("header_encryption", [False, True])
def test_detected_7z_encryption_is_unsupported(
    tmp_path: Path, header_encryption: bool
) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(
        tmp_path / "source.7z",
        [("data", b"secret")],
        password="test-only",
        header_encryption=header_encryption,
    )
    with pytest.raises(UnsupportedFormatError):
        open_7z_backend(p)
    p.unlink()


def test_bad_7z_open_releases_source_and_preserves_cause(tmp_path: Path) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = tmp_path / "bad.7z"
    p.write_bytes(b"not 7z")
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        with pytest.raises(InvalidArchiveError) as error:
            open_7z_backend(p)
    assert error.value.__cause__ is not None and handle.closed
    with pytest.raises(FileNotFoundError):
        open_7z_backend(tmp_path / "missing")


def test_7z_directory_is_ignored_and_symlink_rejected(tmp_path: Path) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    directory = tmp_path / "folder"
    directory.mkdir()
    p = tmp_path / "source.7z"
    with py7zr.SevenZipFile(p, "w") as archive:
        archive.write(directory, "folder")
        archive.writestr(b"data", "folder/payload")
    reader = open_7z_backend(p)
    try:
        assert reader.read(99) == b"data"
        assert reader.read(1) == b""
    finally:
        reader.close()
    target = tmp_path / "target"
    target.write_bytes(b"data")
    link = tmp_path / "link"
    link.symlink_to(target)
    with py7zr.SevenZipFile(p, "w", dereference=False) as archive:
        archive.write(link, "link")
    with pytest.raises(ArchiveStructureError):
        open_7z_backend(p)


@pytest.mark.parametrize(
    "method",
    [py7zr.FILTER_LZMA2, py7zr.FILTER_COPY, py7zr.FILTER_DEFLATE, py7zr.FILTER_BZIP2],
)
def test_real_selected_7z_codecs(tmp_path: Path, method: int) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    payload = b"a\n\0\xff" * 10000
    p = make_7z(tmp_path / "source.7z", [("data", payload)], filters=[{"id": method}])
    reader = open_7z_backend(p)
    try:
        result = bytearray()
        while data := reader.read(103):
            result.extend(data)
        assert bytes(result) == payload and reader.completed
    finally:
        reader.close()


def test_forward_writer_is_thread_safe_and_nonseekable() -> None:
    import io
    import threading

    from archive_stream.backends.sevenzip import _ForwardWriter

    class Endpoint:
        def __init__(self) -> None:
            self.data = bytearray()

        def check_cancelled(self) -> None:
            pass

        def send(self, data: bytes | bytearray | memoryview, /) -> int:
            self.data.extend(data)
            return len(data)

    endpoint = Endpoint()
    writer = _ForwardWriter(endpoint)
    workers = [
        threading.Thread(target=writer.write, args=(part,)) for part in [b"abc", b"def"]
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(2)
        assert not worker.is_alive()
    assert bytes(endpoint.data) in (b"abcdef", b"defabc")
    assert writer.size() == 6 and not writer.seekable()
    with pytest.raises(io.UnsupportedOperation):
        writer.seek(0)
    with pytest.raises(io.UnsupportedOperation):
        writer.read()
    writer.close()
    with pytest.raises(ValueError):
        writer.write(b"x")


def test_missing_extraction_codec_preserves_unsupported_cause(tmp_path: Path) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(tmp_path / "source.7z", [("data", b"data")])
    with patch.object(
        py7zr.SevenZipFile, "extract", side_effect=ImportError("selected codec")
    ):
        reader = open_7z_backend(p)
        try:
            with pytest.raises(UnsupportedFormatError) as error:
                reader.read(1)
            assert isinstance(error.value.__cause__, ImportError)
        finally:
            reader.close()


@pytest.mark.parametrize("allocation", ["_Owner", "_Source"])
def test_opening_allocation_failure_releases_owned_file(
    tmp_path: Path, allocation: str
) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(tmp_path / "source.7z", [("data", b"x")])
    handle = p.open("rb")
    with (
        patch.object(Path, "open", return_value=handle),
        patch(
            "archive_stream.backends.sevenzip." + allocation,
            side_effect=MemoryError("allocation"),
        ),
    ):
        with pytest.raises(MemoryError):
            open_7z_backend(p)
    try:
        assert handle.closed
    finally:
        handle.close()


@pytest.mark.parametrize("operation", ["read", "seek", "tell"])
def test_real_dependency_source_io_failure_stays_ordinary(
    tmp_path: Path, operation: str
) -> None:
    from archive_stream.backends.sevenzip import open_7z_backend

    p = make_7z(tmp_path / "source.7z", [("data", b"payload\n")])
    source = p.open("rb")
    failure = PermissionError("source " + operation)
    original = py7zr.SevenZipFile.extract

    def extract(
        archive: py7zr.SevenZipFile, *, targets: object = None, factory: object = None
    ) -> None:
        with patch.object(source, operation, side_effect=failure):
            original(archive, targets=targets, factory=factory)

    with (
        patch.object(Path, "open", return_value=source),
        patch.object(py7zr.SevenZipFile, "extract", extract),
    ):
        reader = open_7z_backend(p)
        try:
            with pytest.raises(PermissionError) as error:
                reader.read(1)
            assert error.value is failure
        finally:
            reader.close()
    assert source.closed
