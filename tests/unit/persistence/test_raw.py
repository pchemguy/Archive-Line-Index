"""Tests for the headerless little-endian raw index format."""

from __future__ import annotations

from array import array
import inspect
import struct

import pytest

from archive_line_index.errors import InvalidIndexError, PersistenceError
from archive_line_index.offsets import MAX_OFFSET
from archive_line_index.persistence import raw as raw_persistence


def _offsets(*values: int) -> array:
    return array("Q", values)


@pytest.mark.parametrize(
    "values",
    [[0], [3], [0, 2, 5, MAX_OFFSET], list(range(0, 20_000, 2))],
)
def test_write_produces_exact_little_endian_bytes(tmp_path, values: list[int]) -> None:
    destination = tmp_path / "index.raw"
    offsets = _offsets(*values)
    before = offsets.tobytes()

    raw_persistence.write_raw_index(offsets, destination)

    expected = b"".join(struct.pack("<Q", value) for value in values)
    assert destination.read_bytes() == expected
    assert offsets.tobytes() == before


def test_big_endian_encoding_uses_swapped_copy_without_mutating_input() -> None:
    offsets = _offsets(0, 0x0102030405060708)
    before = offsets.tobytes()

    encoded = raw_persistence._encode_little_endian(offsets, byteorder="big")

    assert encoded == struct.pack("<QQ", 0, 0x0102030405060708)
    assert offsets.tobytes() == before


def test_existing_destination_is_protected_without_temporary_file(tmp_path) -> None:
    destination = tmp_path / "index.raw"
    destination.write_bytes(b"original")

    with pytest.raises(FileExistsError):
        raw_persistence.write_raw_index(_offsets(0), destination)

    assert destination.read_bytes() == b"original"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


def test_overwrite_replaces_entire_existing_file(tmp_path) -> None:
    destination = tmp_path / "index.raw"
    destination.write_bytes(b"original")

    raw_persistence.write_raw_index(_offsets(0, 4), destination, overwrite=True)

    assert destination.read_bytes() == struct.pack("<QQ", 0, 4)


@pytest.mark.parametrize(
    "offsets",
    [array("Q"), _offsets(1), _offsets(0, 0), _offsets(0, MAX_OFFSET + 1)],
)
def test_invalid_offsets_fail_before_temporary_creation(
    tmp_path, monkeypatch, offsets: array
) -> None:
    def unexpected_temp(*args, **kwargs):
        raise AssertionError("temporary file created before validation")

    monkeypatch.setattr(raw_persistence.tempfile, "mkstemp", unexpected_temp)

    with pytest.raises(InvalidIndexError):
        raw_persistence.write_raw_index(offsets, tmp_path / "index.raw")


@pytest.mark.parametrize("overwrite", [None, 0, 1, "yes"])
def test_overwrite_must_be_bool(tmp_path, overwrite) -> None:
    with pytest.raises(TypeError, match="overwrite"):
        raw_persistence.write_raw_index(
            _offsets(0), tmp_path / "index.raw", overwrite=overwrite
        )


def test_write_all_accepts_partial_writes() -> None:
    class PartialWriter:
        def __init__(self) -> None:
            self.data = bytearray()

        def write(self, data) -> int:
            count = min(3, len(data))
            self.data.extend(data[:count])
            return count

    writer = PartialWriter()
    raw_persistence._write_all(writer, b"abcdefgh")
    assert bytes(writer.data) == b"abcdefgh"


def test_write_all_rejects_zero_progress() -> None:
    class StalledWriter:
        def write(self, data) -> int:
            return 0

    with pytest.raises(PersistenceError, match="complete"):
        raw_persistence._write_all(StalledWriter(), b"data")


@pytest.mark.parametrize("stage", ["write", "publish"])
def test_prepublication_failure_preserves_destination_and_cleans_temp(
    tmp_path, monkeypatch, stage: str
) -> None:
    destination = tmp_path / "index.raw"
    destination.write_bytes(b"original")
    failure = OSError(f"controlled {stage} failure")
    target = "_write_temporary" if stage == "write" else "_publish"
    monkeypatch.setattr(
        raw_persistence,
        target,
        lambda *args, **kwargs: (_ for _ in ()).throw(failure),
    )

    with pytest.raises(OSError) as captured:
        raw_persistence.write_raw_index(
            _offsets(0, 4), destination, overwrite=True
        )

    assert captured.value is failure
    assert destination.read_bytes() == b"original"
    assert {path.name for path in tmp_path.iterdir()} == {destination.name}


def test_missing_destination_directory_raises_ordinary_os_error(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        raw_persistence.write_raw_index(
            _offsets(0), tmp_path / "missing" / "index.raw"
        )


@pytest.mark.parametrize("values", [[0], [3], [0, 4, 9, MAX_OFFSET]])
def test_read_round_trips_written_file(tmp_path, values: list[int]) -> None:
    path = tmp_path / "index.raw"
    raw_persistence.write_raw_index(_offsets(*values), path)

    loaded = raw_persistence.read_raw_index(path)

    assert loaded.typecode == "Q"
    assert loaded.itemsize == 8
    assert list(loaded) == values


def test_read_missing_file_raises_file_not_found(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        raw_persistence.read_raw_index(tmp_path / "missing.raw")


@pytest.mark.parametrize("content", [b"", b"\0", b"\0" * 7, b"\0" * 9])
def test_read_rejects_empty_or_misaligned_file(tmp_path, content: bytes) -> None:
    path = tmp_path / "index.raw"
    path.write_bytes(content)

    with pytest.raises(InvalidIndexError, match="size"):
        raw_persistence.read_raw_index(path)


@pytest.mark.parametrize(
    "values",
    [[1], [0, 0], [0, 5, 4], [0, MAX_OFFSET + 1]],
)
def test_read_rejects_invalid_decoded_offsets(tmp_path, values: list[int]) -> None:
    path = tmp_path / "index.raw"
    path.write_bytes(b"".join(struct.pack("<Q", value) for value in values))

    with pytest.raises(InvalidIndexError):
        raw_persistence.read_raw_index(path)


def test_big_endian_decode_reconstructs_values() -> None:
    data = struct.pack("<QQQ", 0, 4, 9)

    decoded = raw_persistence._decode_little_endian(data, byteorder="big")

    assert decoded.typecode == "Q"
    assert list(decoded) == [0, 4, 9]


def test_read_error_retains_specific_os_exception(tmp_path, monkeypatch) -> None:
    path = tmp_path / "index.raw"
    path.write_bytes(struct.pack("<Q", 0))
    failure = PermissionError("controlled read failure")

    def fail_read(*args, **kwargs):
        raise failure

    monkeypatch.setattr(raw_persistence, "_read_bytes", fail_read)

    with pytest.raises(PermissionError) as captured:
        raw_persistence.read_raw_index(path)

    assert captured.value is failure


def test_raw_reader_does_not_use_or_expose_mmap() -> None:
    assert "mmap" not in inspect.getsource(raw_persistence)
    assert not hasattr(raw_persistence, "mmap")
