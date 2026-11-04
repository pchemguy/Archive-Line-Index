"""Actual 7z fixture creation shared by unit and integration checks."""

from pathlib import Path

import py7zr


def make_7z(
    path: Path,
    entries: list[tuple[str, bytes]],
    *,
    password: str | None = None,
    header_encryption: bool = False,
    filters: list[dict[str, int]] | None = None,
) -> Path:
    with py7zr.SevenZipFile(
        path,
        "w",
        password=password,
        header_encryption=header_encryption,
        filters=filters,
    ) as archive:
        for name, data in entries:
            archive.writestr(data, name)
    return path
