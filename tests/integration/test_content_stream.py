"""Integration tests for opening plain content streams."""

from __future__ import annotations

import io

import pytest

from archive_line_index import (
    ContentStream,
    SizeLimitExceededError,
    UnsupportedFormatError,
    open_content_stream,
)


def test_path_source_streams_bytes_and_closes_with_context(tmp_path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_bytes(b"first\nsecond")

    with open_content_stream(path) as stream:
        assert isinstance(stream, ContentStream)
        assert stream.read(3) == b"fir"
        assert stream.read() == b"st\nsecond"

    assert stream.closed


def test_caller_stream_starts_at_current_position_and_remains_open() -> None:
    source = io.BytesIO(b"ignoredpayload")
    source.seek(len(b"ignored"))

    with open_content_stream(source) as stream:
        assert stream.read() == b"payload"

    assert not source.closed


def test_consumer_exception_closes_content_stream_not_caller_stream() -> None:
    source = io.BytesIO(b"payload")

    with pytest.raises(RuntimeError, match="consumer"):
        with open_content_stream(source) as stream:
            assert stream.read(1) == b"p"
            raise RuntimeError("consumer failed")

    assert stream.closed
    assert not source.closed


def test_exact_maximum_size_is_allowed() -> None:
    source = io.BytesIO(b"payload")
    with open_content_stream(source, max_uncompressed_size=7) as stream:
        assert stream.read() == b"payload"
    assert not source.closed


def test_size_limit_failure_preserves_caller_ownership() -> None:
    source = io.BytesIO(b"payload")
    with pytest.raises(SizeLimitExceededError, match="declared"):
        open_content_stream(source, max_uncompressed_size=6)
    assert not source.closed


@pytest.mark.parametrize("limit", [True, -1, 1.5, "7"])
def test_invalid_size_limit_fails_before_path_open(tmp_path, limit) -> None:
    missing = tmp_path / "missing.jsonl"
    with pytest.raises((TypeError, ValueError)):
        open_content_stream(missing, max_uncompressed_size=limit)


@pytest.mark.parametrize(
    "signature",
    [b"PK\x03\x04", b"7z\xbc\xaf\x27\x1c", b"\x1f\x8b"],
)
def test_archive_candidates_are_rejected_during_mvp(signature: bytes) -> None:
    source = io.BytesIO(signature + b"not-an-archive")
    with pytest.raises(UnsupportedFormatError):
        open_content_stream(source)
    assert not source.closed
