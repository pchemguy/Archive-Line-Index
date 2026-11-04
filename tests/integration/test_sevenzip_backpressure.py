"""Actual py7zr extraction demonstrates bounded progress and terminal cleanup."""

import hashlib
import threading
from pathlib import Path
from unittest.mock import patch

import py7zr
import pytest
from tests.helpers.sevenzip import make_7z
from tests.integration.test_sevenzip_stream import owned_threads

from archive_line_index import ExtractionError, InvalidArchiveError, open_content_stream
from archive_line_index.backends.producer import _Endpoint


@pytest.mark.timeout(30)
def test_real_slow_consumer_progresses_before_producer_completion(
    tmp_path: Path,
) -> None:
    payload = bytes(range(256)) * (3 * 4096) + b"end"
    target = make_7z(tmp_path / "large.7z", [("data", payload)])
    callback_sizes: list[int] = []
    original = _Endpoint.send

    def observe(endpoint: _Endpoint, data: bytes | bytearray | memoryview, /) -> int:
        callback_sizes.append(len(data))
        return original(endpoint, data)

    before = owned_threads()
    with patch.object(_Endpoint, "send", observe):
        stream = open_content_stream(target)
        bridge = stream._reader._reader
        try:
            first = stream.read(1024)
            assert first == payload[:1024]
            with bridge._endpoint.condition:
                assert bridge._endpoint.condition.wait_for(
                    lambda: len(bridge._endpoint.blocks) == 1, timeout=2
                )
                assert all(
                    len(block.data) <= 1024 * 1024 for block in bridge._endpoint.blocks
                )
                assert bridge._endpoint.terminal is None
                assert len(bridge._current) <= 1024 * 1024
            assert bridge._thread.is_alive() and not bridge._thread.daemon
            digest = hashlib.sha256(first)
            while block := stream.read(64 * 1024):
                digest.update(block)
                threading.Event().wait(0.001)
            assert digest.digest() == hashlib.sha256(payload).digest()
            assert bridge.completed
        finally:
            stream.close()
    assert callback_sizes and sum(callback_sizes) == len(payload)
    assert owned_threads() == before


@pytest.mark.parametrize("prefix_size", [0, 1])
def test_real_full_queue_early_close_joins_and_closes_source(
    tmp_path: Path, prefix_size: int
) -> None:
    payload = b"x\ny" * (1024 * 1024)
    target = make_7z(tmp_path / "large.7z", [("data", payload)])
    before = owned_threads()
    stream = open_content_stream(target)
    backend = stream._reader
    bridge = backend._reader
    source = backend._owner.source
    try:
        if prefix_size:
            assert stream.read(prefix_size) == payload[:prefix_size]
        with bridge._endpoint.condition:
            assert bridge._endpoint.condition.wait_for(
                lambda: len(bridge._endpoint.blocks) == 1, timeout=2
            )
        assert bridge._thread.is_alive()
    finally:
        stream.close()
    assert stream.closed and source.closed
    assert backend._owner.source is None and backend._owner.archive is None
    assert not bridge._thread.is_alive() and not bridge._endpoint.blocks
    assert owned_threads() == before


def test_real_late_crc_and_truncated_archive_cleanup(tmp_path: Path) -> None:
    payload = b"a\nb" * (1024 * 1024)
    target = make_7z(
        tmp_path / "bad.7z", [("data", payload)], filters=[{"id": py7zr.FILTER_COPY}]
    )
    valid = target.read_bytes()
    raw = bytearray(valid)
    raw[32 + len(payload) - 1] ^= 1
    target.write_bytes(raw)
    before = owned_threads()
    stream = open_content_stream(target)
    backend = stream._reader
    bridge = backend._reader
    source = backend._owner.source
    try:
        assert stream.read(1) == b"a"
        with pytest.raises(ExtractionError) as error:
            stream.read()
        assert isinstance(error.value.__cause__, py7zr.exceptions.CrcError)
    finally:
        stream.close()
    assert source.closed and not bridge._thread.is_alive()
    assert owned_threads() == before
    target.write_bytes(valid[:-12])
    with pytest.raises(InvalidArchiveError) as error:
        open_content_stream(target)
    assert error.value.__cause__ is not None
    assert owned_threads() == before
