"""Bounded immutable payload transport with independent cancellation/outcomes.

Only the 7z adapter consumes this bridge. Package-owned waits check cancellation
within 0.05 seconds; cancellation never needs a free slot for a queue sentinel.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .base import BackendReader, validate_positive_size


@dataclass(frozen=True)
class DataBlock:
    """One bounded immutable payload block."""

    data: bytes


@dataclass(frozen=True)
class Finished:
    """The producer and mandatory completion work returned successfully."""


@dataclass(frozen=True)
class Failed:
    """The producer failed after any preceding queued payload blocks."""

    error: BaseException


ProducerMessage = DataBlock | Finished | Failed


class QueueProducer(Protocol):
    """Callback-facing bounded send and cancellation check interface."""

    def send(self, data: bytes | bytearray | memoryview, /) -> int: ...

    def check_cancelled(self) -> None: ...


class _Cancelled(Exception):
    """Internal requested shutdown; never a successful EOF or extraction error."""


def _positive(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


class _Endpoint:
    """Serialize callback blocks through a finite condition-protected queue."""

    def __init__(self, *, queue_capacity: int, block_size: int) -> None:
        _positive(queue_capacity, "queue_capacity")
        _positive(block_size, "block_size")
        self.condition = threading.Condition()
        self.blocks: deque[DataBlock] = deque()
        self.terminal: Finished | Failed | None = None
        self.cancelled = False
        self._capacity = queue_capacity
        self._block_size = block_size
        self._sending = threading.Lock()

    def check_cancelled(self) -> None:
        with self.condition:
            if self.cancelled:
                raise _Cancelled("Payload extraction cancelled")

    def send(self, data: bytes | bytearray | memoryview, /) -> int:
        """Snapshot and enqueue finite blocks without copying a whole callback."""
        with memoryview(data) as original, original.cast("B") as view, self._sending:
            for start in range(0, len(view), self._block_size):
                with self.condition:
                    while len(self.blocks) >= self._capacity and not self.cancelled:
                        self.condition.wait(0.05)
                    self.check_cancelled()
                    if self.terminal is not None:
                        raise RuntimeError("Producer already completed")
                    self.blocks.append(
                        DataBlock(bytes(view[start : start + self._block_size]))
                    )
                    self.condition.notify_all()
            self.check_cancelled()
            return len(view)

    def finish(self, error: BaseException | None) -> None:
        """Publish one terminal outcome independently of data-queue capacity."""
        with self.condition:
            if self.cancelled:
                return
            if self.terminal is not None:
                raise RuntimeError("Producer already completed")
            self.terminal = Finished() if error is None else Failed(error)
            self.condition.notify_all()

    def receive(self) -> ProducerMessage:
        """Keep FIFO payload before terminal success/failure; wake on cancel."""
        with self.condition:
            while not self.blocks and self.terminal is None and not self.cancelled:
                self.condition.wait(0.05)
            self.check_cancelled()
            if self.blocks:
                result = self.blocks.popleft()
                self.condition.notify_all()
                return result
            assert self.terminal is not None
            return self.terminal

    def cancel(self) -> None:
        """Abandon buffered data and wake all package-controlled waits."""
        with self.condition:
            self.cancelled = True
            self.blocks.clear()
            self.terminal = None
            self.condition.notify_all()


class _QueueReader:
    """Deliver one current block and join the owned worker on successful close."""

    def __init__(
        self, endpoint: _Endpoint, worker: threading.Thread, declared_size: int | None
    ) -> None:
        self._endpoint = endpoint
        self._thread = worker
        self.declared_size = declared_size
        self.completed = False
        self._closed = False
        self._failure: BaseException | None = None
        self._current = b""
        self._offset = 0
        self._closing = threading.Lock()

    def read(self, size: int, /) -> bytes:
        if self._closed:
            raise ValueError("read from closed producer reader")
        validate_positive_size(size)
        if self._failure is not None:
            raise self._failure
        if self.completed:
            return b""
        if not self._current:
            try:
                outcome = self._endpoint.receive()
            except _Cancelled:
                raise ValueError("producer reader is closing") from None
            if isinstance(outcome, Failed):
                self._failure = outcome.error
                raise outcome.error
            if isinstance(outcome, Finished):
                self.completed = True
                return b""
            self._current = outcome.data
            self._offset = 0
        end = min(len(self._current), self._offset + size)
        result = self._current[self._offset : end]
        self._offset = end
        if end == len(self._current):
            self._current = b""
            self._offset = 0
        return result

    def close(self) -> None:
        with self._closing:
            if self._closed:
                return
            self._endpoint.cancel()
            self._current = b""
            self._offset = 0
            self._thread.join()
            self._failure = None
            self._closed = True


def start_queue_reader(
    producer: Callable[[QueueProducer], None],
    *,
    declared_size: int | None,
    queue_capacity: int,
    block_size: int,
) -> BackendReader:
    """Start one non-daemon extraction worker and return its owned reader.

    All options are checked before thread startup. The callback owns its acquired
    extraction resources while running and must unwind them on every exit.
    A failed startup cancels/joins any worker actually launched before raising.
    """
    endpoint = _Endpoint(queue_capacity=queue_capacity, block_size=block_size)
    if declared_size is not None:
        if isinstance(declared_size, bool) or not isinstance(declared_size, int):
            raise TypeError("declared_size must be an integer or None")
        if declared_size < 0:
            raise ValueError("declared_size must be nonnegative")
    if not callable(producer):
        raise TypeError("producer must be callable")

    def run() -> None:
        try:
            producer(endpoint)
        except _Cancelled as error:
            if not endpoint.cancelled:
                endpoint.finish(error)
        except BaseException as error:
            endpoint.finish(error)
        else:
            endpoint.finish(None)

    worker = threading.Thread(target=run, name="ali-7z-extract", daemon=False)
    reader = _QueueReader(endpoint, worker, declared_size)
    try:
        worker.start()
    except BaseException:
        endpoint.cancel()
        if worker.ident is not None:
            worker.join()
        raise
    return reader
