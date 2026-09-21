"""Sequential streaming of one validated ZIP regular-file member."""

from __future__ import annotations

import stat
import zipfile

from ..errors import (
    ArchiveStructureError,
    ExtractionError,
    InvalidArchiveError,
)
from ..sources import SourceHandle


class ZipBackendReader:
    """Expose a validated ZIP member through the backend reader contract."""

    def __init__(self, source: SourceHandle) -> None:
        self._source = source
        self._archive: zipfile.ZipFile | None = None
        self._member = None
        self._closed = False
        self._completed = False
        self._declared_size: int | None = None

        if not source.seekable():
            source.close()
            raise InvalidArchiveError("ZIP input must be seekable")

        try:
            self._archive = zipfile.ZipFile(source, "r")
            selected = _select_member(self._archive.infolist())
            self._declared_size = selected.file_size
            try:
                self._member = self._archive.open(selected, "r", pwd=None)
            except RuntimeError as exc:
                raise InvalidArchiveError("ZIP member could not be opened") from exc
        except ArchiveStructureError:
            self.close()
            raise
        except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError) as exc:
            self.close()
            raise InvalidArchiveError("invalid ZIP archive") from exc
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
        assert self._member is not None
        try:
            data = self._member.read(size)
        except RuntimeError as exc:
            self.close()
            raise ExtractionError("ZIP member extraction failed") from exc
        except (zipfile.BadZipFile, EOFError, OSError) as exc:
            self.close()
            raise ExtractionError("ZIP member extraction failed") from exc
        if not isinstance(data, bytes):
            self.close()
            raise ExtractionError("ZIP member returned non-bytes data")
        if not data:
            self._completed = True
        return data

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        member, archive = self._member, self._archive
        self._member = None
        self._archive = None
        try:
            if member is not None:
                member.close()
        finally:
            try:
                if archive is not None:
                    archive.close()
            finally:
                self._source.close()


def open_zip_backend(source: SourceHandle) -> ZipBackendReader:
    """Open and validate a ZIP source without extracting to disk."""

    return ZipBackendReader(source)


def _select_member(entries: list[zipfile.ZipInfo]) -> zipfile.ZipInfo:
    regular: list[zipfile.ZipInfo] = []
    for entry in entries:
        if entry.is_dir():
            continue
        mode = entry.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if file_type not in (0, stat.S_IFREG):
            raise ArchiveStructureError(
                f"unsupported ZIP entry type: {entry.filename!r}"
            )
        regular.append(entry)

    if len(regular) != 1:
        raise ArchiveStructureError(
            f"ZIP archive must contain exactly one regular file; found {len(regular)}"
        )
    return regular[0]
