"""Classify sources using bounded content evidence before filename suffixes."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FormatKind(Enum):
    """Required source families, independent of adapter availability."""

    PLAIN = "plain"
    ZIP = "zip"
    TAR = "tar"
    SEVEN_Z = "7z"


@dataclass(frozen=True)
class FormatCandidate:
    """Resolved candidate with separate content and suffix evidence."""

    kind: FormatKind
    signature_kind: FormatKind | None
    suffix_kind: FormatKind | None


def _signature(prefix: bytes) -> FormatKind | None:
    if prefix.startswith(b"7z\xbc\xaf\x27\x1c"):
        return FormatKind.SEVEN_Z
    if prefix.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return FormatKind.ZIP
    if prefix.startswith((b"\x1f\x8b", b"BZh", b"\xfd7zXZ\x00")):
        return FormatKind.TAR
    if len(prefix) == 512 and any(prefix):
        try:
            checksum = int(prefix[148:156].strip(b"\0 "), 8)
        except ValueError:
            return None
        if checksum == sum(prefix[:148]) + 8 * 32 + sum(prefix[156:]):
            return FormatKind.TAR
    return None


def detect_format(path: Path) -> FormatCandidate:
    """Read at most 512 bytes and select a candidate; do not parse an archive."""
    with path.open("rb") as source:
        signature = _signature(source.read(512))
    name = path.name.lower()
    suffix = None
    if name.endswith(".zip"):
        suffix = FormatKind.ZIP
    elif name.endswith(".7z"):
        suffix = FormatKind.SEVEN_Z
    elif name.endswith(
        (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz", ".tbz2", ".tar.xz", ".txz")
    ):
        suffix = FormatKind.TAR
    return FormatCandidate(signature or suffix or FormatKind.PLAIN, signature, suffix)
