"""Deterministic owned reader outcomes and cleanup fault injection."""

from collections import deque


class Reader:
    """A bounded reader with observable progress and one-shot cleanup faults."""

    def __init__(
        self,
        *events: bytes | BaseException,
        declared_size: int | None = None,
        terminal: bool = True,
        close_failures: int = 0,
    ) -> None:
        self.events = deque(events)
        self.declared_size = declared_size
        self.completed = False
        self.terminal = terminal
        self.close_failures = close_failures
        self.closes = 0
        self.requests: list[int] = []

    def read(self, size: int, /) -> bytes:
        self.requests.append(size)
        event = self.events.popleft() if self.events else b""
        if isinstance(event, BaseException):
            raise event
        if len(event) > size:
            self.events.appendleft(event[size:])
            event = event[:size]
        if not event:
            self.completed = self.terminal
        return event

    def close(self) -> None:
        self.closes += 1
        if self.close_failures:
            self.close_failures -= 1
            raise OSError("close fault")
