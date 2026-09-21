"""Sequential streaming of one validated TAR regular-file member."""

from __future__ import annotations

import tarfile

from ..errors import ArchiveStructureError, ExtractionError, InvalidArchiveError
from ..sources import SourceHandle


_TAR_ERRORS = (tarfile.TarError, EOFError)


class TarBackendReader:
    """Expose one TAR member through a single sequential streaming path."""

    def __init__(self, source: SourceHandle) -> None:
        self._source = source
        self._archive: tarfile.TarFile | None = None
        self._member_stream = None
        self._closed = False
        self._completed = False
        self._declared_size: int | None = None
        self._remaining = 0

        try:
            self._archive = tarfile.open(
                fileobj=_FullReadAdapter(source),
                mode="r|*",
            )
            selected = _find_first_stream_member(self._archive)
            self._declared_size = selected.size
            self._remaining = selected.size
            self._member_stream = self._archive.extractfile(selected)
            if self._member_stream is None:
                raise ArchiveStructureError(
                    f"TAR regular member could not be opened: {selected.name!r}"
                )
        except ArchiveStructureError:
            self.close()
            raise
        except _TAR_ERRORS as exc:
            self.close()
            raise InvalidArchiveError("invalid TAR archive") from exc
        except BaseException:
            self.close()
            raise

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
        if self._completed:
            return b""
        if self._remaining == 0:
            self._validate_stream_tail()
            self._completed = True
            return b""
        assert self._member_stream is not None
        try:
            requested = min(size, self._remaining)
            data = self._member_stream.read(requested)
        except (tarfile.TarError, EOFError, OSError) as exc:
            self.close()
            raise ExtractionError("TAR member extraction failed") from exc
        if not isinstance(data, bytes):
            self.close()
            raise ExtractionError("TAR member returned non-bytes data")
        if not data:
            self.close()
            raise ExtractionError("TAR member ended before its declared size")
        self._remaining -= len(data)
        return data

    def _validate_stream_tail(self) -> None:
        assert self._archive is not None
        try:
            while (entry := self._archive.next()) is not None:
                if entry.isdir():
                    continue
                if entry.isfile():
                    raise ArchiveStructureError(
                        "TAR archive must contain exactly one regular file; "
                        "found an additional member " + repr(entry.name)
                    )
                raise ArchiveStructureError(
                    f"unsupported TAR entry type: {entry.name!r}"
                )
        except ArchiveStructureError:
            self.close()
            raise
        except (tarfile.TarError, EOFError, OSError) as exc:
            self.close()
            raise ExtractionError("TAR trailing validation failed") from exc

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        member_stream, archive = self._member_stream, self._archive
        self._member_stream = None
        self._archive = None
        try:
            if member_stream is not None:
                member_stream.close()
        finally:
            try:
                if archive is not None:
                    archive.close()
            finally:
                self._source.close()


def open_tar_backend(source: SourceHandle) -> TarBackendReader:
    """Open a TAR-family source through sequential streaming mode."""

    return TarBackendReader(source)


def _find_first_stream_member(archive: tarfile.TarFile) -> tarfile.TarInfo:
    while (entry := archive.next()) is not None:
        if entry.isdir():
            continue
        if not entry.isfile():
            raise ArchiveStructureError(
                f"unsupported TAR entry type: {entry.name!r}"
            )
        return entry
    raise ArchiveStructureError(
        "TAR archive must contain exactly one regular file; found 0"
    )


class _FullReadAdapter:
    """Coalesce legal short reads for tarfile's streaming transport."""

    def __init__(self, source: SourceHandle) -> None:
        self._source = source

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self._source.read()
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = self._source.read(remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def close(self) -> None:
        pass
