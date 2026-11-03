"""Raw exact little-endian encoding, corruption and publication outcomes."""

from __future__ import annotations

import struct
from array import array
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.errors import InvalidIndexError
from archive_line_index.persistence.raw import read_raw_index, write_raw_index


@pytest.mark.parametrize(
    "values", [[0], [3], [0, 3], [3, 7, 9], [0, (1 << 63) - 1], list(range(10000))]
)
def test_exact_roundtrip_and_independent_array(
    tmp_path: Path, values: list[int]
) -> None:
    offsets = array("Q", values)
    before = offsets.tobytes()
    path = tmp_path / "index.u64"
    write_raw_index(offsets, path)
    assert path.read_bytes() == b"".join(struct.pack("<Q", v) for v in values)
    restored = read_raw_index(str(path))
    assert restored == offsets and restored is not offsets
    assert restored.typecode == "Q" and restored.itemsize == 8
    assert offsets.tobytes() == before
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"x",
        b"\0" * 9,
        struct.pack("<Q", 1),
        struct.pack("<QQ", 0, 0),
        struct.pack("<QQQ", 0, 5, 4),
        struct.pack("<QQ", 0, 1 << 63),
    ],
)
def test_malformed_raw_is_not_modified(tmp_path: Path, data: bytes) -> None:
    path = tmp_path / "bad"
    path.write_bytes(data)
    with pytest.raises(InvalidIndexError):
        read_raw_index(path)
    assert path.read_bytes() == data


@pytest.mark.parametrize(
    "offsets,overwrite,exc",
    [
        (array("Q"), False, InvalidIndexError),
        (array("I", [0]), False, TypeError),
        (array("Q", [0]), 1, TypeError),
    ],
)
def test_invalid_inputs_before_allocation(
    tmp_path: Path, offsets: object, overwrite: object, exc: type[Exception]
) -> None:
    with (
        patch(
            "archive_line_index.persistence.raw.temporary_sibling",
            side_effect=AssertionError("temporary allocated"),
        ),
        pytest.raises(exc),
    ):
        write_raw_index(offsets, tmp_path / "p", overwrite=overwrite)  # type: ignore[arg-type]
    assert not list(tmp_path.iterdir())


def test_protection_replacement_and_prepublication_failure(tmp_path: Path) -> None:
    path = tmp_path / "p"
    path.write_bytes(b"previous")
    with (
        patch(
            "archive_line_index.persistence.raw.temporary_sibling",
            side_effect=AssertionError("temporary allocated"),
        ),
        pytest.raises(FileExistsError),
    ):
        write_raw_index(array("Q", [0]), path)
    with (
        patch(
            "archive_line_index.persistence.raw.publish_index_file",
            side_effect=OSError("publish fault"),
        ),
        pytest.raises(OSError, match="publish fault"),
    ):
        write_raw_index(array("Q", [0]), path, overwrite=True)
    assert path.read_bytes() == b"previous" and list(tmp_path.iterdir()) == [path]
    write_raw_index(array("Q", [3]), path, overwrite=True)
    assert read_raw_index(path).tolist() == [3]


def test_postpublication_cleanup_failure_retains_complete_destination(
    tmp_path: Path,
) -> None:
    path = tmp_path / "p"
    with (
        patch.object(Path, "unlink", side_effect=PermissionError("cleanup fault")),
        pytest.raises(PermissionError) as caught,
    ):
        write_raw_index(array("Q", [0, 9]), path)
    assert read_raw_index(path).tolist() == [0, 9]
    assert any(
        "Publication already succeeded" in n and str(path) in n
        for n in caught.value.__notes__
    )
    for temporary in tmp_path.glob(".*.tmp"):
        temporary.unlink()


def test_opposite_endian_conversion_preserves_input(tmp_path: Path) -> None:
    class BigEndianArray(array):
        def tobytes(self) -> bytes:
            return b"".join(struct.pack(">Q", v) for v in self)

    offsets = BigEndianArray("Q", [0, 3, 512])
    before = offsets.tolist()
    with patch("archive_line_index.persistence.raw._BYTEORDER", "big"):
        write_raw_index(offsets, tmp_path / "p")
    assert (tmp_path / "p").read_bytes() == struct.pack("<QQQ", 0, 3, 512)
    assert offsets.tolist() == before


def test_missing_path_remains_filesystem_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_raw_index(tmp_path / "missing")


def test_write_error_remains_primary_when_file_close_also_fails(tmp_path: Path) -> None:
    import io

    class FaultyFile(io.BytesIO):
        def write(self, data: object) -> int:
            raise OSError("write primary")

        def close(self) -> None:
            raise OSError("close cleanup")

    handle = FaultyFile()
    with patch.object(Path, "open", return_value=handle):
        with pytest.raises(OSError, match="write primary") as caught:
            write_raw_index(array("Q", [0]), tmp_path / "p")
    assert any("close cleanup" in note for note in caught.value.__notes__)
    assert not list(tmp_path.iterdir())
    io.BytesIO.close(handle)


def test_partial_writes_are_completed_and_zero_progress_is_rejected() -> None:
    import io

    from archive_line_index.persistence.raw import _write_all

    class Short(io.BytesIO):
        def write(self, data: object) -> int:
            return super().write(memoryview(data)[:2])  # type: ignore[arg-type]

    with Short() as handle:
        _write_all(handle, b"abcdef")
        assert handle.getvalue() == b"abcdef"

    class Stalled(io.BytesIO):
        def write(self, data: object) -> int:
            return 0

    with Stalled() as handle, pytest.raises(OSError, match="Incomplete"):
        _write_all(handle, b"x")


def test_opposite_endian_reader_conversion(tmp_path: Path) -> None:
    class BigNativeArray(array):
        def frombytes(self, data: bytes) -> None:
            super().frombytes(data)
            self.byteswap()

    path = tmp_path / "p"
    path.write_bytes(struct.pack("<QQQ", 0, 3, 512))
    with (
        patch("archive_line_index.persistence.raw._BYTEORDER", "big"),
        patch("archive_line_index.persistence.raw.array", BigNativeArray),
    ):
        assert read_raw_index(path).tolist() == [0, 3, 512]


def test_incomplete_stable_read_rejected_and_handle_closed(tmp_path: Path) -> None:
    import io
    from types import SimpleNamespace

    class ShortFile(io.BytesIO):
        def fileno(self) -> int:
            return 17

    handle = ShortFile(struct.pack("<Q", 0))
    with (
        patch.object(Path, "open", return_value=handle),
        patch(
            "archive_line_index.persistence.raw.os.fstat",
            return_value=SimpleNamespace(st_size=16),
        ),
        pytest.raises(InvalidIndexError, match="Incomplete"),
    ):
        read_raw_index(tmp_path / "p")
    assert handle.closed
