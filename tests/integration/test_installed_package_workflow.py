"""Self-contained workflow runnable against source or an isolated wheel install."""

from __future__ import annotations

from array import array
import io
from pathlib import Path
import tarfile
import tempfile
import zipfile

import py7zr

from archive_line_index import (
    build_line_index,
    open_content_stream,
    read_raw_index,
    read_sqlite_index,
    write_raw_index,
    write_sqlite_index,
)


PAYLOAD = b"\xef\xbb\xbfalpha\nbeta\nomega"
EXPECTED_OFFSETS = array("Q", [3, 9, 14, 19])


def _make_sources(directory: Path) -> list[Path]:
    plain = directory / "payload.bin"
    plain.write_bytes(PAYLOAD)

    zip_path = directory / "payload.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nested/payload.jsonl", PAYLOAD)

    tar_path = directory / "payload.tar.gz"
    with tarfile.open(tar_path, "w:gz") as archive:
        info = tarfile.TarInfo("nested/payload.jsonl")
        info.size = len(PAYLOAD)
        archive.addfile(info, io.BytesIO(PAYLOAD))

    sevenzip_path = directory / "payload.7z"
    with py7zr.SevenZipFile(sevenzip_path, "w") as archive:
        archive.writestr(PAYLOAD, "nested/payload.jsonl")

    return [plain, zip_path, tar_path, sevenzip_path]


def run_workflow(directory: Path) -> None:
    """Exercise every public workflow without repository-local helpers."""

    sources = _make_sources(directory)
    initial_names = {path.name for path in directory.iterdir()}

    indexes = []
    for source in sources:
        chunks = []
        with open_content_stream(source) as stream:
            while chunk := stream.read(7):
                chunks.append(chunk)
        assert b"".join(chunks) == PAYLOAD
        indexes.append(build_line_index(source, buffer_size=5))

    assert all(index == EXPECTED_OFFSETS for index in indexes)

    sqlite_path = directory / "index.sqlite"
    raw_path = directory / "index.u64"
    write_sqlite_index(indexes[0], sqlite_path)
    write_raw_index(indexes[0], raw_path)
    assert read_sqlite_index(sqlite_path) == EXPECTED_OFFSETS
    assert read_raw_index(raw_path) == EXPECTED_OFFSETS

    for source in sources:
        stream = open_content_stream(source)
        assert stream.read(4) == PAYLOAD[:4]
        stream.close()
        stream.close()
        assert stream.closed

    assert {path.name for path in directory.iterdir()} == initial_names | {
        sqlite_path.name,
        raw_path.name,
    }


def test_complete_public_workflow(tmp_path) -> None:
    run_workflow(tmp_path)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporary:
        run_workflow(Path(temporary))
    print("installed package workflow passed")
