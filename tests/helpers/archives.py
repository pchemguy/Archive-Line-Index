"""Actual TAR/ZIP fixtures; tests choose exposed members and metadata faults."""

import io
import struct
import tarfile
import zipfile
import zlib
from pathlib import Path


def make_tar(
    path: Path,
    entries: list[tuple[str, bytes, bytes]],
    *,
    mode: str = "w",
    format: int = tarfile.PAX_FORMAT,
) -> Path:
    """Write archive bytes without extracting any member paths."""
    with tarfile.open(path, mode, format=format) as archive:
        for name, data, kind in entries:
            info = tarfile.TarInfo(name)
            info.type = kind
            if kind in (tarfile.LNKTYPE, tarfile.SYMTYPE):
                info.linkname = "target"
            info.size = len(data) if info.isreg() else 0
            archive.addfile(info, io.BytesIO(data) if info.isreg() else None)
    return path


def make_zip_with_size_metadata(
    path: Path,
    payload: bytes,
    declared_size: int,
    *,
    compression: int = zipfile.ZIP_DEFLATED,
    crc_payload: bytes | None = None,
) -> Path:
    """Change both real ZIP size headers, optionally setting a deliberate CRC."""
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        archive.writestr("data", payload)
    raw = bytearray(path.read_bytes())
    local = raw.index(b"PK\x03\x04")
    central = raw.index(b"PK\x01\x02")
    struct.pack_into("<I", raw, local + 22, declared_size)
    struct.pack_into("<I", raw, central + 24, declared_size)
    if crc_payload is not None:
        crc = zlib.crc32(crc_payload)
        struct.pack_into("<I", raw, local + 14, crc)
        struct.pack_into("<I", raw, central + 16, crc)
    path.write_bytes(raw)
    return path
