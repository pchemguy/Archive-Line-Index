"""ZIP metadata validation uses real archives and rejects unsafe member kinds."""

import stat
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.errors import (
    ArchiveStructureError,
    InvalidArchiveError,
    UnsupportedFormatError,
)


def make_zip(path: Path, entries: list[tuple[str, bytes, int]]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data, mode in entries:
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = mode << 16
            archive.writestr(info, data)
    return path


@pytest.mark.parametrize("payload", [b"", b"a\n\xff"])
def test_sole_nested_regular_member(tmp_path: Path, payload: bytes) -> None:
    from archive_line_index.backends.zip import open_zip_backend

    p = make_zip(
        tmp_path / "a.zip",
        [("folder/", b"", stat.S_IFDIR), ("../folder/data", payload, stat.S_IFREG)],
    )
    reader = open_zip_backend(p)
    assert reader.declared_size == len(payload)
    reader.close()
    reader.close()
    assert sorted(x.name for x in tmp_path.iterdir()) == ["a.zip"]
    p.unlink()


@pytest.mark.parametrize(
    "names", [[], ["folder/"], ["a", "b"], ["a", "__MACOSX/metadata"]]
)
def test_invalid_member_counts(tmp_path: Path, names: list[str]) -> None:
    from archive_line_index.backends.zip import open_zip_backend

    p = make_zip(
        tmp_path / "a.zip",
        [(n, b"", stat.S_IFDIR if n.endswith("/") else stat.S_IFREG) for n in names],
    )
    with pytest.raises(ArchiveStructureError):
        open_zip_backend(p)
    p.unlink()


@pytest.mark.parametrize(
    "kind", [stat.S_IFLNK, stat.S_IFIFO, stat.S_IFSOCK, stat.S_IFCHR, stat.S_IFBLK]
)
def test_special_metadata_is_not_a_regular_file(tmp_path: Path, kind: int) -> None:
    from archive_line_index.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("special", b"target", kind)])
    with pytest.raises(ArchiveStructureError):
        open_zip_backend(p)
    p.unlink()


def test_detected_encryption_is_unsupported(tmp_path: Path) -> None:
    from archive_line_index.backends.zip import open_zip_backend

    p = make_zip(tmp_path / "a.zip", [("a", b"secret", stat.S_IFREG)])
    data = bytearray(p.read_bytes())
    # Set the encryption flag in both actual ZIP headers; no password is supplied.
    for signature, offset in [(b"PK\x03\x04", 6), (b"PK\x01\x02", 8)]:
        data[data.index(signature) + offset] |= 1
    p.write_bytes(data)
    with pytest.raises(UnsupportedFormatError):
        open_zip_backend(p)
    p.unlink()


def test_invalid_open_preserves_cause_and_releases_source(tmp_path: Path) -> None:
    from archive_line_index.backends.zip import open_zip_backend

    p = tmp_path / "bad.zip"
    p.write_bytes(b"not ZIP")
    handle = p.open("rb")
    with patch.object(Path, "open", return_value=handle):
        with pytest.raises(InvalidArchiveError) as error:
            open_zip_backend(p)
    assert isinstance(error.value.__cause__, zipfile.BadZipFile)
    assert handle.closed
    with pytest.raises(FileNotFoundError):
        open_zip_backend(tmp_path / "missing")
