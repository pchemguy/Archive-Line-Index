"""Owned sequential TAR payload access without filesystem member extraction.

TAR is consumed in stream mode. The adapter owns all acquired handles and never
uses a member name as a filesystem destination.
"""

from __future__ import annotations

import tarfile
from pathlib import Path
from typing import IO, Protocol, Self

from ..errors import ArchiveStructureError, ExtractionError, InvalidArchiveError
from .base import BackendReader, validate_positive_size


class _StrictTarInfo(tarfile.TarInfo):
    """Do not let tarfile's permissive iterator hide damaged later headers."""

    @classmethod
    def fromtarfile(cls, archive: tarfile.TarFile) -> Self:
        try:
            return super().fromtarfile(archive)
        except tarfile.HeaderError as error:
            # tarfile exposes this concrete subtype at runtime but omits it from
            # its public type stubs. Only a complete zero pair is terminal EOF.
            if isinstance(error, tarfile.EOFHeaderError):  # type: ignore[attr-defined]
                if archive.fileobj.read(512) != b"\0" * 512:
                    raise tarfile.ReadError("Incomplete TAR end marker") from error
                raise
            raise tarfile.ReadError("Invalid or truncated TAR header") from error


class _Closable(Protocol):
    def close(self) -> None: ...


def _close_resources(resources: list[_Closable]) -> None:
    failure: BaseException | None = None
    for resource in resources[:]:
        try:
            resource.close()
        except BaseException as error:
            if failure is None:
                failure = error
            else:
                failure.add_note(f"TAR cleanup failed: {error!r}")
        else:
            resources.remove(resource)
    if failure is not None:
        raise failure


def _first_payload(archive: tarfile.TarFile) -> tarfile.TarInfo:
    while (member := archive.next()) is not None:
        # Python 3.11/3.12 retain parsed metadata even in stream mode.
        archive.members.clear()  # type: ignore[attr-defined]
        if member.isdir():
            continue
        if not member.isreg():
            raise ArchiveStructureError("TAR contains a special member")
        return member
    raise ArchiveStructureError("TAR must contain exactly one regular file")


class _TarReader:
    def __init__(
        self,
        member: IO[bytes],
        resources: list[_Closable],
        declared_size: int,
        archive: tarfile.TarFile,
    ) -> None:
        self._member = member
        self._archive = archive
        self._resources = resources
        self.declared_size = declared_size
        self.completed = False

    def read(self, size: int, /) -> bytes:
        validate_positive_size(size)
        if self.completed:
            return b""
        try:
            data = self._member.read(size)
            if not data:
                self._finish()
            return data
        except tarfile.TarError as error:
            raise ExtractionError("TAR payload delivery failed") from error

    def _finish(self) -> None:
        while (member := self._archive.next()) is not None:
            self._archive.members.clear()  # type: ignore[attr-defined]
            if not member.isdir():
                raise ArchiveStructureError(
                    "TAR contains an additional or special member"
                )
        while padding := self._archive.fileobj.read(64 * 1024):
            if any(padding):
                raise ExtractionError(
                    "TAR contains non-padding bytes after its end marker"
                )
        self.completed = True

    def close(self) -> None:
        _close_resources(self._resources)


def open_tar_backend(path: Path) -> BackendReader:
    """Open a regular payload in sequential plain-TAR mode, owning all handles."""
    source = path.open("rb")
    resources: list[_Closable] = [source]
    try:
        try:
            archive = tarfile.open(fileobj=source, mode="r|", tarinfo=_StrictTarInfo)
            resources.insert(0, archive)
            info = _first_payload(archive)
            member = archive.extractfile(info)
            if member is None:
                raise ArchiveStructureError("TAR payload is not readable")
            resources.insert(0, member)
        except tarfile.TarError as error:
            raise InvalidArchiveError("Cannot open TAR payload") from error
        return _TarReader(member, resources, info.size, archive)
    except BaseException as error:
        try:
            _close_resources(resources)
        except BaseException as cleanup:
            error.add_note(f"TAR opening cleanup failed: {cleanup!r}")
        raise
