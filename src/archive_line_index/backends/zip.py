"""Single-member ZIP metadata selection and owned sequential payload access.

Member names are never used as filesystem paths. The source, archive and member
handles remain owned by the returned backend until explicit closure.
"""

from __future__ import annotations

import stat
import zipfile
from pathlib import Path
from typing import IO, Protocol

from ..errors import ArchiveStructureError, InvalidArchiveError, UnsupportedFormatError
from .base import BackendReader, validate_positive_size


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
                failure.add_note(f"ZIP cleanup failed: {error!r}")
        else:
            resources.remove(resource)
    if failure is not None:
        raise failure


def _select_member(archive: zipfile.ZipFile) -> zipfile.ZipInfo:
    members = []
    for info in archive.infolist():
        if info.flag_bits & (1 | 64):
            raise UnsupportedFormatError("Encrypted ZIP members are unsupported")
        kind = stat.S_IFMT(info.external_attr >> 16)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ArchiveStructureError("ZIP contains a special member")
        if info.is_dir() or kind == stat.S_IFDIR or info.external_attr & 0x10:
            continue
        members.append(info)
    if len(members) != 1:
        raise ArchiveStructureError("ZIP must contain exactly one regular file")
    return members[0]


class _ZipReader:
    def __init__(
        self, member: IO[bytes], resources: list[_Closable], declared_size: int
    ) -> None:
        self._member = member
        self._resources = resources
        self.declared_size = declared_size
        self.completed = False

    def read(self, size: int, /) -> bytes:
        validate_positive_size(size)
        data = self._member.read(size)
        if not data:
            self.completed = True
        return data

    def close(self) -> None:
        _close_resources(self._resources)


def open_zip_backend(path: Path) -> BackendReader:
    """Open a sole regular ZIP member, releasing all handles on opening failure.

    Malformed opening retains its dependency cause as InvalidArchiveError.
    Encryption and unavailable compression are unsupported features; source
    filesystem failures retain their ordinary Python types.
    """
    source = path.open("rb")
    resources: list[_Closable] = [source]
    try:
        try:
            archive = zipfile.ZipFile(source)
            resources.insert(0, archive)
            info = _select_member(archive)
            member = archive.open(info)
            resources.insert(0, member)
        except (zipfile.BadZipFile, EOFError, ValueError) as error:
            raise InvalidArchiveError("Cannot open ZIP payload") from error
        except (NotImplementedError, RuntimeError) as error:
            raise UnsupportedFormatError("ZIP compression is unavailable") from error
        return _ZipReader(member, resources, info.file_size)
    except BaseException as error:
        try:
            _close_resources(resources)
        except BaseException as cleanup:
            error.add_note(f"ZIP opening cleanup failed: {cleanup!r}")
        raise
