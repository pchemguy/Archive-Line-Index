"""Tests for the bounded 7z push-to-pull queue protocol."""

from __future__ import annotations

import io
import queue
import threading
from types import SimpleNamespace

import pytest
import py7zr

from archive_line_index.backends.sevenzip import (
    _CALLBACK_BLOCK_SIZE,
    _Payload,
    _QueueBackendReader,
    _QueueProducer,
    _QueueWriter,
    _SelectedWriterFactory,
    _extract_member,
    open_sevenzip_backend,
)
from archive_line_index.errors import (
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    SizeLimitExceededError,
)
from archive_line_index.stream import ContentStream
from tests.helpers.archive_factory import ArchiveMember, write_7z


def _payload_producer(chunks):
    def produce(channel) -> None:
        for chunk in chunks:
            channel.send(chunk)

    return produce


def test_arbitrary_reads_split_and_coalesce_producer_blocks() -> None:
    reader = _QueueBackendReader(_payload_producer([b"ab", b"cdef", b"ghi"]))
    assert reader.read(1) == b"a"
    assert reader.read(5) == b"bcdef"
    assert reader.read(10) == b"ghi"
    assert reader.read(10) == b""
    assert reader.completed
    reader.close()


def test_callback_input_is_subdivided_at_one_mebibyte() -> None:
    content = b"x" * (_CALLBACK_BLOCK_SIZE + 17)
    messages: queue.Queue[object] = queue.Queue(maxsize=3)
    producer = _QueueProducer(messages, threading.Event())

    assert producer.send(content) == len(content)

    first = messages.get_nowait()
    second = messages.get_nowait()
    assert isinstance(first, _Payload)
    assert isinstance(second, _Payload)
    assert len(first.data) == _CALLBACK_BLOCK_SIZE
    assert len(second.data) == 17
    assert messages.empty()


def test_one_slot_queue_applies_slow_consumer_backpressure() -> None:
    attempted_second_put = threading.Event()
    sent_all = threading.Event()

    def produce(channel) -> None:
        original_put = channel._put
        put_count = 0

        def observed_put(message) -> None:
            nonlocal put_count
            put_count += 1
            if put_count == 2:
                attempted_second_put.set()
            original_put(message)

        channel._put = observed_put
        channel.send(b"a")
        channel.send(b"b")
        channel.send(b"c")
        sent_all.set()

    reader = _QueueBackendReader(produce)
    try:
        assert attempted_second_put.wait(1)
        assert reader._messages.qsize() == 1
        assert not sent_all.is_set()
        assert reader.read(1) == b"a"
        assert reader.read(1) == b"b"
        assert reader.read(1) == b"c"
        assert sent_all.wait(1)
        assert reader.read(1) == b""
    finally:
        reader.close()


def test_failure_after_prefix_is_raised_on_next_progress_read() -> None:
    failure = OSError("controlled worker failure")

    def produce(channel) -> None:
        channel.send(b"prefix")
        raise failure

    reader = _QueueBackendReader(produce)
    assert reader.read(64) == b"prefix"
    with pytest.raises(ExtractionError) as captured:
        reader.read(1)
    assert captured.value.__cause__ is failure
    assert not reader._worker.is_alive()


def test_close_unblocks_blocked_producer_and_joins_worker() -> None:
    attempted_second_put = threading.Event()
    exited = threading.Event()

    def produce(channel) -> None:
        original_put = channel._put
        put_count = 0

        def observed_put(message) -> None:
            nonlocal put_count
            put_count += 1
            if put_count == 2:
                attempted_second_put.set()
            original_put(message)

        channel._put = observed_put
        try:
            channel.send(b"a")
            channel.send(b"b")
        finally:
            exited.set()

    reader = _QueueBackendReader(produce)
    assert attempted_second_put.wait(1)
    assert reader._messages.qsize() == 1
    reader.close()
    assert exited.wait(1)
    assert not reader._worker.is_alive()


def test_close_is_idempotent_and_abandons_queued_failure() -> None:
    def produce(channel) -> None:
        raise RuntimeError("abandoned")

    reader = _QueueBackendReader(produce)
    reader.close()
    reader.close()
    assert not reader._worker.is_alive()
    with pytest.raises(ValueError):
        reader.read(1)


def test_declared_size_is_exposed_without_producer_progress() -> None:
    gate = threading.Event()

    def produce(channel) -> None:
        while not gate.is_set():
            channel.check_cancelled()
            gate.wait(0.01)

    reader = _QueueBackendReader(produce, declared_size=7)
    assert reader.declared_size == 7
    reader.close()


@pytest.mark.parametrize(
    "size",
    [_CALLBACK_BLOCK_SIZE - 1, _CALLBACK_BLOCK_SIZE, _CALLBACK_BLOCK_SIZE + 1],
)
def test_real_py7zr_destination_streams_callback_sizes(tmp_path, size: int) -> None:
    content = bytes(range(251)) * (size // 251) + bytes(range(size % 251))
    path = write_7z(tmp_path / "data.7z", [ArchiveMember("nested/data", content)])

    def produce(channel) -> None:
        with py7zr.SevenZipFile(path, "r") as archive:
            _extract_member(archive, "nested/data", channel)

    reader = _QueueBackendReader(produce, declared_size=size)
    chunks = []
    while chunk := reader.read(131_071):
        chunks.append(chunk)
    assert b"".join(chunks) == content
    reader.close()


def test_writer_implements_dependency_seek_size_and_close_contract() -> None:
    delivered = []

    class Channel:
        def send(self, data) -> int:
            delivered.append(bytes(data))
            return len(data)

        def check_cancelled(self) -> None:
            pass

    writer = _QueueWriter(Channel())
    assert writer.write(b"abc") == 3
    assert writer.size() == 3
    assert writer.seek(0) == 0
    assert writer.seek(0, 2) == 3
    assert writer.read() == b""
    writer.flush()
    writer.close()
    assert delivered == [b"abc"]
    with pytest.raises(ValueError):
        writer.write(b"x")


def test_factory_rejects_wrong_or_repeated_target() -> None:
    class Channel:
        pass

    factory = _SelectedWriterFactory("wanted", Channel())
    with pytest.raises(RuntimeError, match="unexpected"):
        factory.create("other")
    assert isinstance(factory.create("wanted"), _QueueWriter)
    with pytest.raises(RuntimeError, match="more than once"):
        factory.create("wanted")


def test_writer_preserves_callback_exception_identity() -> None:
    failure = OSError("delivery failed")

    class Channel:
        def send(self, data) -> int:
            raise failure

    writer = _QueueWriter(Channel())
    with pytest.raises(OSError) as captured:
        writer.write(b"data")
    assert captured.value is failure


def test_cancellation_during_large_callback_delivery_joins_worker() -> None:
    attempted_second_put = threading.Event()

    def produce(channel) -> None:
        original_put = channel._put
        put_count = 0

        def observed_put(message) -> None:
            nonlocal put_count
            put_count += 1
            if put_count == 2:
                attempted_second_put.set()
            original_put(message)

        channel._put = observed_put
        _QueueWriter(channel).write(b"x" * (_CALLBACK_BLOCK_SIZE * 4))

    reader = _QueueBackendReader(produce)
    assert attempted_second_put.wait(1)
    assert reader._messages.qsize() == 1
    reader.close()
    assert not reader._worker.is_alive()


def _read_backend(path, size: int = 3) -> bytes:
    backend = open_sevenzip_backend(str(path))
    chunks = []
    try:
        while chunk := backend.read(size):
            chunks.append(chunk)
        assert backend.completed
        return b"".join(chunks)
    finally:
        backend.close()


def test_path_streams_nested_member_with_directory(tmp_path) -> None:
    path = write_7z(
        tmp_path / "data.7z",
        [
            ArchiveMember("nested", kind="directory"),
            ArchiveMember("nested/data.jsonl", b"a\nb"),
        ],
    )
    assert _read_backend(path, 1) == b"a\nb"


def test_empty_member_is_valid(tmp_path) -> None:
    path = write_7z(tmp_path / "empty.7z", [ArchiveMember("empty", b"")])
    backend = open_sevenzip_backend(str(path))
    assert backend.declared_size == 0
    assert backend.read(1) == b""
    assert backend.completed
    backend.close()


@pytest.mark.parametrize(
    "members",
    [
        [ArchiveMember("directory", kind="directory")],
        [ArchiveMember("a", b"a"), ArchiveMember("b", b"b")],
        [ArchiveMember("data", b"x"), ArchiveMember("__MACOSX/meta", b"m")],
    ],
)
def test_zero_multiple_and_metadata_files_are_rejected(tmp_path, members) -> None:
    path = write_7z(tmp_path / "structure.7z", members)
    with pytest.raises(ArchiveStructureError, match="exactly one"):
        open_sevenzip_backend(str(path))


def test_invalid_and_truncated_archives_are_open_failures(tmp_path) -> None:
    invalid = tmp_path / "invalid.7z"
    invalid.write_bytes(b"7z\xbc\xaf\x27\x1cnot-an-archive")
    with pytest.raises(InvalidArchiveError):
        open_sevenzip_backend(str(invalid))

    valid = write_7z(
        tmp_path / "valid.7z",
        [ArchiveMember("data", b"payload" * 100)],
    )
    truncated = tmp_path / "truncated.7z"
    content = valid.read_bytes()
    truncated.write_bytes(content[: len(content) // 2])
    with pytest.raises(InvalidArchiveError):
        open_sevenzip_backend(str(truncated))


def test_declared_size_limit_closes_backend_and_joins_worker(tmp_path) -> None:
    path = write_7z(tmp_path / "data.7z", [ArchiveMember("data", b"payload")])
    backend = open_sevenzip_backend(str(path))
    with pytest.raises(SizeLimitExceededError, match="declared"):
        ContentStream(backend, max_uncompressed_size=6)
    assert not backend._reader._worker.is_alive()


def test_early_close_joins_worker(tmp_path) -> None:
    content = b"x" * (_CALLBACK_BLOCK_SIZE * 3)
    path = write_7z(tmp_path / "data.7z", [ArchiveMember("data", content)])
    backend = open_sevenzip_backend(str(path))
    assert backend.read(1) == b"x"
    backend.close()
    backend.close()
    assert not backend._reader._worker.is_alive()


def test_worker_start_failure_closes_open_archive(monkeypatch) -> None:
    class Archive:
        closed = False

        def list(self):
            return [
                SimpleNamespace(
                    filename="data",
                    is_directory=False,
                    is_symlink=False,
                    is_file=True,
                    uncompressed=7,
                )
            ]

        def close(self) -> None:
            self.closed = True

    archive = Archive()
    failure = RuntimeError("thread start failed")

    monkeypatch.setattr(
        "archive_line_index.backends.sevenzip.py7zr.SevenZipFile",
        lambda *args, **kwargs: archive,
    )

    def fail_reader(*args, **kwargs):
        raise failure

    monkeypatch.setattr(
        "archive_line_index.backends.sevenzip._QueueBackendReader",
        fail_reader,
    )

    with pytest.raises(RuntimeError) as captured:
        open_sevenzip_backend("data.7z")

    assert captured.value is failure
    assert archive.closed
