"""Cross-backend deterministic resource and ownership integration tests."""

from __future__ import annotations

import builtins
import io
import os

import pytest

from archive_line_index import (
    InvalidArchiveError,
    SizeLimitExceededError,
    open_content_stream,
)
from tests.helpers.archive_factory import ArchiveMember, write_7z, write_tar, write_zip


FORMATS = ("plain", "zip", "tar", "sevenzip")


def _make_source(tmp_path, source_format: str, content: bytes):
    if source_format == "plain":
        path = tmp_path / "data.jsonl"
        path.write_bytes(content)
        return path
    if source_format == "zip":
        return write_zip(
            tmp_path / "data.zip",
            [ArchiveMember("nested/data", content)],
        )
    if source_format == "tar":
        return write_tar(
            tmp_path / "data.tgz",
            [ArchiveMember("nested/data", content)],
        )
    if source_format == "sevenzip":
        return write_7z(
            tmp_path / "data.7z",
            [ArchiveMember("nested/data", content)],
        )
    raise AssertionError(source_format)


@pytest.mark.parametrize("source_format", FORMATS)
def test_normal_exhaustion_closes_package_resources_not_caller(
    tmp_path, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"payload")
    caller = io.BytesIO(path.read_bytes())
    with open_content_stream(caller) as stream:
        assert stream.read() == b"payload"
        assert stream.read(1) == b""
        if source_format == "sevenzip":
            assert not stream._backend._reader._worker.is_alive()
    assert stream.closed
    assert not caller.closed


@pytest.mark.parametrize("source_format", FORMATS)
def test_early_and_repeated_close_preserve_caller(
    tmp_path, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"x" * (3 * 1024 * 1024))
    caller = io.BytesIO(path.read_bytes())
    stream = open_content_stream(caller)
    assert stream.read(1) == b"x"
    stream.close()
    stream.close()
    assert not caller.closed
    if source_format == "sevenzip":
        assert not stream._backend._reader._worker.is_alive()


@pytest.mark.parametrize("source_format", FORMATS)
def test_context_exit_after_consumer_exception_releases_resources(
    tmp_path, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"payload")
    caller = io.BytesIO(path.read_bytes())
    with pytest.raises(RuntimeError, match="consumer"):
        with open_content_stream(caller) as stream:
            assert stream.read(1) == b"p"
            raise RuntimeError("consumer failure")
    assert stream.closed
    assert not caller.closed
    if source_format == "sevenzip":
        assert not stream._backend._reader._worker.is_alive()


@pytest.mark.parametrize("source_format", FORMATS)
def test_declared_size_failure_preserves_caller_and_joins_worker(
    tmp_path, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"payload")
    caller = io.BytesIO(path.read_bytes())
    with pytest.raises(SizeLimitExceededError):
        open_content_stream(caller, max_uncompressed_size=6)
    assert not caller.closed


@pytest.mark.parametrize(
    "content",
    [b"PK\x03\x04broken", b"\x1f\x8bbroken", b"7z\xbc\xaf\x27\x1cbroken"],
)
def test_invalid_archive_failure_preserves_caller(content: bytes) -> None:
    caller = io.BytesIO(content)
    with pytest.raises(InvalidArchiveError):
        open_content_stream(caller)
    assert not caller.closed


@pytest.mark.parametrize("source_format", FORMATS)
def test_path_owned_source_file_is_closed_after_exhaustion(
    tmp_path, monkeypatch, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"payload")
    opened = []
    original_open = builtins.open

    def tracking_open(file, mode="r", *args, **kwargs):
        result = original_open(file, mode, *args, **kwargs)
        if os.fspath(file) == os.fspath(path) and mode == "rb":
            opened.append(result)
        return result

    monkeypatch.setattr(builtins, "open", tracking_open)
    with open_content_stream(path) as stream:
        assert stream.read() == b"payload"
    assert len(opened) == 1
    assert opened[0].closed


@pytest.mark.parametrize("source_format", FORMATS)
def test_backend_creates_no_decompressed_member_artifact(
    tmp_path, source_format: str
) -> None:
    path = _make_source(tmp_path, source_format, b"payload")
    before = {item.name for item in tmp_path.iterdir()}
    with open_content_stream(path) as stream:
        assert stream.read() == b"payload"
    assert {item.name for item in tmp_path.iterdir()} == before
