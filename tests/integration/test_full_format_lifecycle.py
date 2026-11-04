"""Cross-format fidelity, independent instances and actual exceptional cleanup."""

import os
import signal
import tarfile
import threading
import zipfile
from array import array
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.helpers.archives import make_tar
from tests.helpers.sevenzip import make_7z
from tests.integration.test_sevenzip_stream import owned_threads

from archive_line_index import (
    SizeLimitExceededError,
    build_line_index,
    open_content_stream,
)

KINDS = ["plain", "zip", "tar", "gz", "bz2", "xz", "7z"]


def make_source(root: Path, kind: str, key: str, payload: bytes) -> Path:
    suffix = (
        ".tar"
        if kind == "tar"
        else ".tar." + kind
        if kind in ("gz", "bz2", "xz")
        else "." + kind
    )
    p = root / (key + suffix)
    if kind == "plain":
        p.write_bytes(payload)
    elif kind == "zip":
        with zipfile.ZipFile(p, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("nested/data", payload)
    elif kind == "7z":
        make_7z(p, [("nested/data", payload)])
    else:
        make_tar(
            p,
            [("nested/data", payload, tarfile.REGTYPE)],
            mode="w" if kind == "tar" else "w:" + kind,
        )
    return p


@pytest.mark.parametrize("kind", KINDS)
def test_independent_simultaneous_instances(tmp_path: Path, kind: str) -> None:
    payloads = [b"left\n" * 1000, b"\xef\xbb\xbfright\r\n\nlast"]
    sources = [
        make_source(tmp_path, kind, str(i), payload)
        for i, payload in enumerate(payloads)
    ]
    barrier = threading.Barrier(2)
    before = owned_threads()

    def read(index: int) -> bytes:
        with open_content_stream(sources[index]) as stream:
            barrier.wait(3)
            prefix = stream.read(1)
            return prefix + stream.read()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert list(executor.map(read, range(2))) == payloads
    assert owned_threads() == before
    for source, payload in zip(sources, payloads, strict=True):
        plain = tmp_path / "reference"
        plain.write_bytes(payload)
        assert build_line_index(source) == build_line_index(plain)


@pytest.mark.parametrize("kind", KINDS)
def test_inclusive_limits_zero_ops_and_nonbyte_buffer_capacity(
    tmp_path: Path, kind: str
) -> None:
    source = make_source(tmp_path, kind, "data", b"abcdefgh")
    original = source.read_bytes()
    before = owned_threads()
    with open_content_stream(source, max_uncompressed_size=8) as stream:
        with patch.object(
            stream._reader,
            "read",
            side_effect=AssertionError("zero operation advanced backend"),
        ):
            assert stream.read(0) == b""
            assert stream.readinto(bytearray()) == 0
        buffer = array("I", [0x3F3F3F3F] * 3)
        assert stream.readinto(buffer) == 8
        assert memoryview(buffer).cast("B").tobytes() == b"abcdefgh????"
        assert stream.read() == b""
    with pytest.raises(SizeLimitExceededError):
        open_content_stream(source, max_uncompressed_size=7)
    assert owned_threads() == before
    assert source.read_bytes() == original
    empty = make_source(tmp_path, kind, "empty", b"")
    with open_content_stream(empty, max_uncompressed_size=0) as stream:
        assert stream.read() == b""
    assert owned_threads() == before


@pytest.mark.parametrize("kind", KINDS)
def test_consumer_exception_preserves_primary_and_closes(
    tmp_path: Path, kind: str
) -> None:
    source = make_source(tmp_path, kind, "data", b"a\nb" * 10000)
    before = owned_threads()
    failure = RuntimeError("consumer")
    stream = open_content_stream(source)
    with pytest.raises(RuntimeError) as error:
        with stream:
            assert stream.read(1) == b"a"
            raise failure
    assert error.value is failure and stream.closed
    assert owned_threads() == before


@pytest.mark.timeout(30)
def test_actual_sigint_during_7z_wait_releases_worker(tmp_path: Path) -> None:
    from archive_line_index.backends.sevenzip import _ForwardWriter

    source = make_7z(tmp_path / "signal.7z", [("data", b"a\nb" * (1024 * 1024))])
    ready = threading.Event()
    waiting = threading.Event()
    release = threading.Event()
    original_write = _ForwardWriter.write
    before = owned_threads()

    def gated(writer: _ForwardWriter, data: bytes | bytearray) -> int:
        ready.set()
        while not release.wait(0.01):
            writer._endpoint.check_cancelled()
        return original_write(writer, data)

    with patch.object(_ForwardWriter, "write", gated):
        stream = open_content_stream(source)
        backend = stream._reader
        bridge = backend._reader
        original_wait = bridge._endpoint.condition.wait

        def observe_wait(timeout: float | None = None) -> bool:
            waiting.set()
            return original_wait(timeout)

        def interrupt() -> None:
            if waiting.wait(2):
                os.kill(os.getpid(), signal.SIGINT)
            else:
                release.set()

        sender = threading.Thread(target=interrupt)
        try:
            assert ready.wait(2)
            with patch.object(bridge._endpoint.condition, "wait", observe_wait):
                sender.start()
                with pytest.raises(KeyboardInterrupt):
                    stream.read()
        finally:
            release.set()
            stream.close()
            if sender.ident is not None:
                sender.join(2)
    assert not sender.is_alive() and not bridge._thread.is_alive()
    assert owned_threads() == before
