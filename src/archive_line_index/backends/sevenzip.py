"""Bounded push-to-pull infrastructure for the 7z backend."""

from __future__ import annotations

import io
import queue
import struct
import threading
from dataclasses import dataclass
from typing import Any, Callable

import py7zr

from ..errors import (
    ArchiveLineIndexError,
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
)
from ..sources import SourceHandle


_CALLBACK_BLOCK_SIZE = 1024 * 1024
_QUEUE_WAIT_SECONDS = 0.05


@dataclass(frozen=True, slots=True)
class _Payload:
    data: bytes


@dataclass(frozen=True, slots=True)
class _Failure:
    error: BaseException


@dataclass(frozen=True, slots=True)
class _Completion:
    pass


_COMPLETION = _Completion()


class _Cancelled(Exception):
    pass


class _QueueProducer:
    """Producer-side channel with cooperative cancellation and subdivision."""

    def __init__(
        self,
        messages: queue.Queue[object],
        cancelled: threading.Event,
    ) -> None:
        self._messages = messages
        self._cancelled = cancelled

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    def send(self, data: bytes | bytearray | memoryview) -> int:
        view = memoryview(data).cast("B")
        total = len(view)
        for start in range(0, total, _CALLBACK_BLOCK_SIZE):
            self.check_cancelled()
            block = bytes(view[start : start + _CALLBACK_BLOCK_SIZE])
            self._put(_Payload(block))
        return total

    def check_cancelled(self) -> None:
        if self.cancelled:
            raise _Cancelled

    def finish(self) -> None:
        self._put(_COMPLETION)

    def fail(self, error: BaseException) -> None:
        self._put(_Failure(error))

    def _put(self, message: object) -> None:
        while True:
            self.check_cancelled()
            try:
                self._messages.put(message, timeout=_QUEUE_WAIT_SECONDS)
                return
            except queue.Full:
                continue


class _QueueWriter(py7zr.io.Py7zIO):
    """Sequential py7zr destination that forwards callback bytes immediately."""

    def __init__(self, channel: _QueueProducer) -> None:
        self._channel = channel
        self._position = 0
        self._written = 0
        self._closed = False

    def write(self, data: bytes | bytearray) -> int:
        if self._closed:
            raise ValueError("I/O operation on closed 7z destination")
        if self._position != self._written:
            raise io.UnsupportedOperation("7z destination is sequential")
        count = self._channel.send(data)
        self._position += count
        self._written += count
        return count

    def read(self, size: int | None = None) -> bytes:
        return b""

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            target = offset
        elif whence == io.SEEK_CUR:
            target = self._position + offset
        elif whence == io.SEEK_END:
            target = self._written + offset
        else:
            raise ValueError(f"invalid whence: {whence}")
        if target not in (0, self._written):
            raise io.UnsupportedOperation("7z destination is sequential")
        self._position = target
        return target

    def flush(self) -> None:
        self._channel.check_cancelled()

    def size(self) -> int:
        return self._written

    def close(self) -> None:
        self._closed = True


class _SelectedWriterFactory(py7zr.io.WriterFactory):
    """Create exactly one queue writer for the prevalidated target member."""

    def __init__(self, target: str, channel: _QueueProducer) -> None:
        self._target = target
        self._channel = channel
        self.writer: _QueueWriter | None = None

    def create(self, filename: str) -> _QueueWriter:
        if filename != self._target:
            raise RuntimeError(f"unexpected 7z extraction target: {filename!r}")
        if self.writer is not None:
            raise RuntimeError("7z extraction destination was created more than once")
        self.writer = _QueueWriter(self._channel)
        return self.writer


def _extract_member(
    archive: py7zr.SevenZipFile,
    target: str,
    channel: _QueueProducer,
) -> None:
    factory = _SelectedWriterFactory(target, channel)
    archive.extract(targets=[target], factory=factory)
    if factory.writer is None:
        raise RuntimeError("py7zr did not create the selected destination")


class _QueueBackendReader:
    """Consumer-side backend reader driven by one bounded producer worker."""

    def __init__(
        self,
        producer: Callable[[_QueueProducer], None],
        *,
        declared_size: int | None = None,
        thread_name: str = "archive-line-index-7z",
    ) -> None:
        self._messages: queue.Queue[object] = queue.Queue(maxsize=1)
        self._cancelled = threading.Event()
        self._channel = _QueueProducer(self._messages, self._cancelled)
        self._declared_size = declared_size
        self._buffer = bytearray()
        self._pending_failure: BaseException | None = None
        self._completed = False
        self._closed = False
        self._worker = threading.Thread(
            target=self._run_producer,
            args=(producer,),
            name=thread_name,
            daemon=False,
        )
        self._worker.start()

    @property
    def declared_size(self) -> int | None:
        return self._declared_size

    @property
    def completed(self) -> bool:
        return self._completed

    def read(self, size: int) -> bytes:
        if self._closed:
            raise ValueError("I/O operation on closed backend")
        if not isinstance(size, int) or isinstance(size, bool):
            raise TypeError("backend read size must be an integer")
        if size <= 0:
            raise ValueError("backend read size must be positive")

        if self._pending_failure is not None and not self._buffer:
            self._raise_pending_failure()

        while len(self._buffer) < size and not self._completed:
            message = self._messages.get()
            if isinstance(message, _Payload):
                self._buffer.extend(message.data)
            elif isinstance(message, _Failure):
                self._pending_failure = message.error
                if not self._buffer:
                    self._raise_pending_failure()
                break
            elif message is _COMPLETION:
                self._completed = True
                self._worker.join()
            else:
                self.close()
                raise ExtractionError("unknown 7z queue message")

        take = min(size, len(self._buffer))
        result = bytes(self._buffer[:take])
        del self._buffer[:take]
        return result

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._cancelled.set()
        self._buffer.clear()
        while self._worker.is_alive():
            try:
                self._messages.get_nowait()
            except queue.Empty:
                pass
            self._worker.join(_QUEUE_WAIT_SECONDS)

    def _run_producer(
        self,
        producer: Callable[[_QueueProducer], None],
    ) -> None:
        try:
            producer(self._channel)
            self._channel.finish()
        except _Cancelled:
            return
        except BaseException as exc:
            try:
                self._channel.fail(exc)
            except _Cancelled:
                return

    def _raise_pending_failure(self) -> None:
        assert self._pending_failure is not None
        error = self._pending_failure
        self._pending_failure = None
        self.close()
        if isinstance(error, ArchiveLineIndexError):
            raise error
        raise ExtractionError("7z extraction worker failed") from error


class SevenZipBackendReader:
    """Inspect one 7z member and stream extraction through a bounded worker."""

    def __init__(self, source: SourceHandle) -> None:
        self._source = source
        self._fileobj = _SourceIO(source)
        self._archive: py7zr.SevenZipFile | None = None
        self._reader: _QueueBackendReader | None = None

        if not source.seekable():
            source.close()
            raise InvalidArchiveError("7z input must be seekable")

        try:
            self._archive = py7zr.SevenZipFile(self._fileobj, "r")
            selected = _select_7z_member(self._archive.list())
        except (py7zr.exceptions.ArchiveError, EOFError, struct.error) as exc:
            self._close_unstarted()
            raise InvalidArchiveError("invalid 7z archive") from exc
        except ArchiveStructureError:
            self._close_unstarted()
            raise
        except BaseException:
            self._close_unstarted()
            raise

        archive = self._archive
        assert archive is not None
        target = selected.filename

        def produce(channel: _QueueProducer) -> None:
            try:
                _extract_member(archive, target, channel)
            except py7zr.exceptions.ArchiveError as exc:
                raise ExtractionError("7z member extraction failed") from exc
            finally:
                try:
                    archive.close()
                finally:
                    try:
                        self._fileobj.close()
                    finally:
                        source.close()

        self._reader = _QueueBackendReader(
            produce,
            declared_size=selected.uncompressed,
        )

    @property
    def declared_size(self) -> int | None:
        assert self._reader is not None
        return self._reader.declared_size

    @property
    def completed(self) -> bool:
        assert self._reader is not None
        return self._reader.completed

    def read(self, size: int) -> bytes:
        assert self._reader is not None
        return self._reader.read(size)

    def close(self) -> None:
        if self._reader is not None:
            self._reader.close()
        else:
            self._close_unstarted()

    def _close_unstarted(self) -> None:
        archive, self._archive = self._archive, None
        try:
            if archive is not None:
                archive.close()
        finally:
            try:
                self._fileobj.close()
            finally:
                self._source.close()


def open_sevenzip_backend(source: SourceHandle) -> SevenZipBackendReader:
    """Open, validate, and begin bounded extraction of a 7z source."""

    return SevenZipBackendReader(source)


def _select_7z_member(entries) -> Any:
    regular = []
    for entry in entries:
        if entry.is_directory:
            continue
        if entry.is_symlink or not entry.is_file:
            raise ArchiveStructureError(
                f"unsupported 7z entry type: {entry.filename!r}"
            )
        regular.append(entry)
    if len(regular) != 1:
        raise ArchiveStructureError(
            f"7z archive must contain exactly one regular file; found {len(regular)}"
        )
    return regular[0]


class _SourceIO(io.RawIOBase):
    """Present a SourceHandle to py7zr without transferring ownership."""

    def __init__(self, source: SourceHandle) -> None:
        super().__init__()
        self._source = source

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return self._source.seekable()

    def read(self, size: int = -1) -> bytes:
        self._checkClosed()
        return self._source.read(size)

    def readinto(self, buffer) -> int:
        self._checkClosed()
        view = memoryview(buffer).cast("B")
        data = self._source.read(len(view))
        view[: len(data)] = data
        return len(data)

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        self._checkClosed()
        return self._source.seek(offset, whence)

    def tell(self) -> int:
        self._checkClosed()
        return self._source.tell()
