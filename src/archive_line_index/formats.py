"""Bounded, content-first input format classification."""

from __future__ import annotations

import os
from enum import Enum
from .sources import Source, normalize_source_path


DETECTION_PREFIX_SIZE = 512

_SEVEN_ZIP_SIGNATURE = b"7z\xbc\xaf\x27\x1c"
_ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
_GZIP_SIGNATURE = b"\x1f\x8b"
_BZIP2_SIGNATURE = b"BZh"
_XZ_SIGNATURE = b"\xfd7zXZ\x00"

_SUFFIXES = (
    (".tar.bz2", "tar"),
    (".tar.gz", "tar"),
    (".tar.xz", "tar"),
    (".tbz2", "tar"),
    (".tgz", "tar"),
    (".tbz", "tar"),
    (".txz", "tar"),
    (".tar", "tar"),
    (".zip", "zip"),
    (".7z", "seven_zip"),
)


class SourceFormat(Enum):
    """Internal candidate selected by signatures and suffix claims."""

    PLAIN = "plain"
    ZIP = "zip"
    TAR = "tar"
    SEVEN_ZIP = "seven_zip"


def detect_format(
    source: Source,
) -> SourceFormat:
    """Classify a source path from a bounded prefix and its suffix."""

    path = normalize_source_path(source)
    with open(path, "rb") as stream:
        prefix = stream.read(DETECTION_PREFIX_SIZE)
    signature_format = _format_from_signature(prefix)
    if signature_format is not None:
        return signature_format

    suffix_format = _format_from_suffix(path)
    if suffix_format is not None:
        return suffix_format
    return SourceFormat.PLAIN


def _format_from_signature(prefix: bytes) -> SourceFormat | None:
    if prefix.startswith(_SEVEN_ZIP_SIGNATURE):
        return SourceFormat.SEVEN_ZIP
    if prefix.startswith(_ZIP_SIGNATURES):
        return SourceFormat.ZIP
    if prefix.startswith((_GZIP_SIGNATURE, _BZIP2_SIGNATURE, _XZ_SIGNATURE)):
        return SourceFormat.TAR
    if _looks_like_tar_header(prefix):
        return SourceFormat.TAR
    return None


def _format_from_suffix(filename: Source) -> SourceFormat | None:
    name = os.fspath(filename)
    if not isinstance(name, str):
        raise TypeError("filename must resolve to str, not bytes")
    lower_name = name.lower()
    for suffix, format_value in _SUFFIXES:
        if lower_name.endswith(suffix):
            return SourceFormat(format_value)
    return None


def _looks_like_tar_header(prefix: bytes) -> bool:
    if len(prefix) < DETECTION_PREFIX_SIZE:
        return False
    header = prefix[:DETECTION_PREFIX_SIZE]
    if not any(header):
        return False

    checksum_field = header[148:156].rstrip(b"\0 ").strip()
    if not checksum_field:
        return False
    try:
        stored_checksum = int(checksum_field, 8)
    except ValueError:
        return False

    calculated_checksum = sum(header[:148]) + (8 * ord(" ")) + sum(header[156:])
    return stored_checksum == calculated_checksum
