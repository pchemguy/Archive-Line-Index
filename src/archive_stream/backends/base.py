"""Owned bounded reader protocol shared by concrete payload adapters."""

from typing import Protocol


class BackendReader(Protocol):
    """Deliver bounded bytes and report validated terminal completion."""

    @property
    def declared_size(self) -> int | None:
        """Trustworthy payload size, or unknown metadata."""
        ...

    @property
    def completed(self) -> bool:
        """Whether successful terminal validation has completed."""
        ...

    def read(self, size: int, /) -> bytes:
        """Return at most size bytes; empty bytes require completed=True."""
        ...

    def close(self) -> None:
        """Release owned resources; retry is allowed after cleanup failure."""
        ...


def validate_positive_size(size: int) -> None:
    """Reject invalid internal read sizes before reader progress."""
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("read size must be an integer")
    if size <= 0:
        raise ValueError("backend read size must be positive")
