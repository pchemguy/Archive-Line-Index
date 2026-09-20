"""Minimal contract between concrete backends and the common content stream."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class BackendReader(Protocol):
    """Sequential backend reader consumed by ``ContentStream``.

    ``read()`` returns terminal ``b""`` only after backend completion and
    integrity work succeeds, at which point ``completed`` is true.
    """

    @property
    def declared_size(self) -> int | None:
        """Return trustworthy payload-size metadata when available."""

        ...

    @property
    def completed(self) -> bool:
        """Return whether successful terminal backend completion occurred."""

        ...

    def read(self, size: int) -> bytes:
        """Return at most ``size`` sequential payload bytes."""

        ...

    def close(self) -> None:
        """Release all resources owned by the backend."""

        ...
