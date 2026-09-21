"""Tests for validated sequential TAR path streaming."""

from __future__ import annotations

import tarfile

import pytest

from archive_line_index.backends.tar import open_tar_backend
from archive_line_index.errors import (
    ArchiveStructureError,
    InvalidArchiveError,
    SizeLimitExceededError,
)
from archive_line_index.stream import ContentStream
from tests.helpers.archive_factory import ArchiveMember, write_tar


def _read_backend(path, size: int = 3) -> bytes:
    backend = open_tar_backend(str(path))
    chunks = []
    try:
        while chunk := backend.read(size):
            chunks.append(chunk)
        assert backend.completed
        return b"".join(chunks)
    finally:
        backend.close()


@pytest.mark.parametrize(
    "filename",
    ["data.tar", "data.tar.gz", "data.tgz", "data.tar.bz2", "data.tbz2", "data.tar.xz", "data.txz"],
)
def test_tar_variants_stream_nested_member(tmp_path, filename: str) -> None:
    path = write_tar(
        tmp_path / filename,
        [
            ArchiveMember("nested", kind="directory"),
            ArchiveMember("nested/data.jsonl", b"a\nb"),
        ],
    )
    assert _read_backend(path, 1) == b"a\nb"


def test_empty_member_is_valid(tmp_path) -> None:
    path = write_tar(tmp_path / "empty.tar", [ArchiveMember("empty", b"")])
    backend = open_tar_backend(str(path))
    assert backend.declared_size == 0
    assert backend.read(1) == b""
    assert backend.completed
    backend.close()


def test_zero_regular_files_are_rejected_before_delivery(tmp_path) -> None:
    path = write_tar(
        tmp_path / "structure.tar",
        [ArchiveMember("directory", kind="directory")],
    )
    with pytest.raises(ArchiveStructureError, match="exactly one"):
        open_tar_backend(str(path))


@pytest.mark.parametrize(
    "members, expected",
    [
        ([ArchiveMember("a", b"a"), ArchiveMember("b", b"b")], b"a"),
        ([ArchiveMember("data", b"x"), ArchiveMember("__MACOSX/meta", b"m")], b"x"),
    ],
)
def test_reports_late_additional_member(tmp_path, members, expected) -> None:
    path = write_tar(tmp_path / "structure.tar", members)
    backend = open_tar_backend(str(path))
    assert backend.read(64) == expected
    with pytest.raises(ArchiveStructureError, match="additional"):
        backend.read(64)


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo"])
def test_reports_late_special_member(tmp_path, kind: str) -> None:
    path = write_tar(
        tmp_path / "special.tar",
        [
            ArchiveMember("data", b"payload"),
            ArchiveMember("special", kind=kind, target="data"),
        ],
    )
    backend = open_tar_backend(str(path))
    assert backend.read(64) == b"payload"
    with pytest.raises(ArchiveStructureError, match="unsupported"):
        backend.read(64)


def test_invalid_archive_is_translated_with_cause(tmp_path) -> None:
    path = tmp_path / "invalid.tar"
    path.write_bytes(b"not-a-tar")
    with pytest.raises(InvalidArchiveError) as captured:
        open_tar_backend(str(path))
    assert isinstance(captured.value.__cause__, tarfile.TarError)


def test_truncated_compressed_archive_is_rejected(tmp_path) -> None:
    valid = write_tar(
        tmp_path / "valid.tgz",
        [ArchiveMember("data", b"payload" * 1000)],
    )
    truncated = tmp_path / "truncated.tgz"
    content = valid.read_bytes()
    truncated.write_bytes(content[: len(content) // 2])
    with pytest.raises(InvalidArchiveError):
        open_tar_backend(str(truncated))


def test_declared_size_limit_closes_backend(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    backend = open_tar_backend(str(path))
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)


def test_early_close_is_idempotent(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    backend = open_tar_backend(str(path))
    assert backend.read(1) == b"p"
    backend.close()
    backend.close()
    with pytest.raises(ValueError):
        backend.read(1)


def test_streaming_tar_creates_no_extraction_artifacts(tmp_path) -> None:
    path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", b"payload")])
    before = {item.name for item in tmp_path.iterdir()}
    assert _read_backend(path) == b"payload"
    assert {item.name for item in tmp_path.iterdir()} == before


def test_initial_member_probe_failure_closes_archive(monkeypatch) -> None:
    class Archive:
        closed = False

        def next(self):
            raise tarfile.ReadError("controlled probe failure")

        def close(self) -> None:
            self.closed = True

    archive = Archive()
    monkeypatch.setattr(
        "archive_line_index.backends.tar.tarfile.open",
        lambda **kwargs: archive,
    )

    with pytest.raises(InvalidArchiveError):
        open_tar_backend("data.tar")

    assert archive.closed
