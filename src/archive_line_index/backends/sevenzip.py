"""Single-payload py7zr callback extraction through the bounded worker bridge.

The source is passed as an owned binary reader, disabling py7zr's parallel file
extraction path. Callback output is forwarded; no member path is materialized.
"""

from __future__ import annotations

import io
import threading
from pathlib import Path
from typing import BinaryIO, cast

import py7zr
from py7zr.exceptions import PasswordRequired, UnsupportedCompressionMethodError
from py7zr.io import Py7zIO, WriterFactory

from ..errors import (
    ArchiveLineIndexError,
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
    UnsupportedFormatError,
)
from .base import BackendReader
from .producer import QueueProducer, start_queue_reader

_BLOCK_SIZE = 1024 * 1024


class _Source(io.RawIOBase):
    """Track underlying filesystem failures separately from dependency errors."""

    def __init__(self, handle: BinaryIO) -> None:
        super().__init__()
        self.handle = handle
        self.failure: OSError | None = None

    def read(self, size: int = -1) -> bytes:
        try:
            return self.handle.read(size)
        except OSError as error:
            self.failure = error
            raise

    def seek(self, offset: int, whence: int = 0) -> int:
        try:
            return self.handle.seek(offset, whence)
        except OSError as error:
            self.failure = error
            raise

    def tell(self) -> int:
        try:
            return self.handle.tell()
        except OSError as error:
            self.failure = error
            raise

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return self.handle.seekable()

    def close(self) -> None:
        if not self.closed:
            self.handle.close()
            super().close()


class _Owner:
    """Close archive/source exactly once successfully; permit failed-close retry."""

    def __init__(self, source: BinaryIO) -> None:
        self.source: BinaryIO | None = source
        self.archive: py7zr.SevenZipFile | None = None
        self._lock = threading.Lock()

    def close(self) -> None:
        with self._lock:
            failure: BaseException | None = None
            for name in ("archive", "source"):
                resource = getattr(self, name)
                if resource is None:
                    continue
                try:
                    resource.close()
                except BaseException as error:
                    if failure is None:
                        failure = error
                    else:
                        failure.add_note(f"7z cleanup failed: {error!r}")
                else:
                    setattr(self, name, None)
            if failure is not None:
                raise failure


class _ForwardWriter(Py7zIO):
    """Thread-safe forward-only callback counter with bounded transport."""

    def __init__(self, endpoint: QueueProducer) -> None:
        self._endpoint = endpoint
        self._lock = threading.Lock()
        self._position = 0
        self._closed = False

    def write(self, data: bytes | bytearray) -> int:
        with self._lock:
            self._endpoint.check_cancelled()
            if self._closed:
                raise ValueError("7z callback writer is closed")
            count = self._endpoint.send(data)
            self._position += count
            return count

    def read(self, size: int | None = None) -> bytes:
        raise io.UnsupportedOperation("7z callback is write-only")

    def seek(self, offset: int, whence: int = 0) -> int:
        with self._lock:
            if (whence == 0 and offset == self._position) or (
                whence in (1, 2) and offset == 0
            ):
                return self._position
            raise io.UnsupportedOperation("7z callback cannot rewind")

    def seekable(self) -> bool:
        return False

    def flush(self) -> None:
        self._endpoint.check_cancelled()

    def size(self) -> int:
        with self._lock:
            return self._position

    def close(self) -> None:
        with self._lock:
            self._closed = True


class _Factory(WriterFactory):
    def __init__(self, writer: _ForwardWriter) -> None:
        self.writer = writer
        self.created = False
        self._lock = threading.Lock()

    def create(self, filename: str) -> Py7zIO:
        with self._lock:
            if self.created:
                raise ExtractionError("7z requested an additional callback writer")
            self.created = True
            return self.writer


class _SevenZipReader:
    def __init__(self, owner: _Owner, size: int) -> None:
        self._owner = owner
        self._reader: BackendReader | None = None
        self.declared_size = size

    @property
    def completed(self) -> bool:
        return self._reader is not None and self._reader.completed

    def read(self, size: int, /) -> bytes:
        assert self._reader is not None
        return self._reader.read(size)

    def close(self) -> None:
        if self._reader is not None:
            self._reader.close()
        self._owner.close()


def _select_member(archive: py7zr.SevenZipFile) -> py7zr.FileInfo:
    if archive.needs_password():
        raise UnsupportedFormatError("Encrypted 7z archives are unsupported")
    members = []
    for info in archive.list():
        if info.is_symlink or not (info.is_file or info.is_directory):
            raise ArchiveStructureError("7z contains a special member")
        if info.is_directory:
            continue
        if info.uncompressed < 0:
            raise InvalidArchiveError("7z declares a negative payload size")
        members.append(info)
    if len(members) != 1:
        raise ArchiveStructureError("7z must contain exactly one regular file")
    return members[0]


def open_7z_backend(path: Path) -> BackendReader:
    """Open one 7z payload and transfer extraction/cleanup to one owned worker.

    Validates member structure before startup. Missing codecs/encryption are
    unsupported; malformed opening and later extraction retain distinct causes.
    The binary source and archive are released on every failed opening path.
    """
    source = path.open("rb")
    try:
        owner = _Owner(source)
    except BaseException as error:
        try:
            source.close()
        except BaseException as cleanup:
            error.add_note(f"7z source cleanup failed: {cleanup!r}")
        raise
    try:
        tracked = _Source(source)
        owner.source = cast(BinaryIO, tracked)
        try:
            archive = py7zr.SevenZipFile(
                cast(BinaryIO, tracked),
                "r",
                blocksize=_BLOCK_SIZE,
                max_extract_size=None,
            )
            owner.archive = archive
            info = _select_member(archive)
        except (
            PasswordRequired,
            UnsupportedCompressionMethodError,
            ImportError,
        ) as error:
            raise UnsupportedFormatError(
                "7z encryption or codec is unsupported"
            ) from error
        except Exception as error:
            if (
                isinstance(error, (ArchiveLineIndexError, MemoryError))
                or error is tracked.failure
            ):
                raise
            raise InvalidArchiveError("Cannot open 7z payload") from error
        reader = _SevenZipReader(owner, info.uncompressed)

        def produce(endpoint: QueueProducer) -> None:
            writer = _ForwardWriter(endpoint)
            factory = _Factory(writer)
            try:
                try:
                    endpoint.check_cancelled()
                    archive.extract(targets=[info.filename], factory=factory)
                    endpoint.check_cancelled()
                    if not factory.created or writer.size() != info.uncompressed:
                        raise ExtractionError(
                            "7z callback size/completion disagrees with metadata"
                        )
                except Exception as error:
                    endpoint.check_cancelled()
                    if (
                        isinstance(error, (ArchiveLineIndexError, MemoryError))
                        or error is tracked.failure
                    ):
                        raise
                    if isinstance(
                        error,
                        (
                            PasswordRequired,
                            UnsupportedCompressionMethodError,
                            ImportError,
                        ),
                    ):
                        raise UnsupportedFormatError(
                            "7z codec is unavailable"
                        ) from error
                    raise ExtractionError(
                        "7z payload delivery or integrity validation failed"
                    ) from error
            except BaseException as error:
                try:
                    owner.close()
                except BaseException as cleanup:
                    error.add_note(f"7z producer cleanup failed: {cleanup!r}")
                raise
            else:
                owner.close()

        reader._reader = start_queue_reader(
            produce,
            declared_size=info.uncompressed,
            queue_capacity=1,
            block_size=_BLOCK_SIZE,
        )
        return reader
    except BaseException as error:
        try:
            owner.close()
        except BaseException as cleanup:
            error.add_note(f"7z opening cleanup failed: {cleanup!r}")
        raise
