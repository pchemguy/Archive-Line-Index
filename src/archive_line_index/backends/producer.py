"""Bounded immutable payload transport with independent cancellation/outcomes.

Only the 7z adapter consumes this bridge. Package-owned waits check cancellation
within 0.05 seconds; cancellation never needs a free slot for a queue sentinel.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Protocol


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
            self.condition.notify_all()
