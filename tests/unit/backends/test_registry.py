"""Tests for backend dispatch."""

import io
import tarfile
import zipfile

import pytest

import archive_line_index.backends as backend_package
from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.registry import open_backend
from archive_line_index.formats import SourceFormat
from archive_line_index.sources import open_source
from tests.helpers.archive_factory import ArchiveMember, write_7z


def test_plain_candidate_dispatches_to_a_reader() -> None:
    reader = open_backend(SourceFormat.PLAIN, open_source(io.BytesIO(b"payload")))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == b"payload"


def test_zip_candidate_dispatches_to_a_reader() -> None:
    source = io.BytesIO()
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("data", b"payload")
    source.seek(0)
    reader = open_backend(SourceFormat.ZIP, open_source(source))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == b"payload"
    reader.close()
    assert not source.closed


def test_tar_candidate_dispatches_to_a_reader() -> None:
    source = io.BytesIO()
    with tarfile.open(fileobj=source, mode="w:") as archive:
        info = tarfile.TarInfo("data")
        info.size = 7
        archive.addfile(info, io.BytesIO(b"payload"))
    source.seek(0)
    reader = open_backend(SourceFormat.TAR, open_source(source))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == b"payload"
    reader.close()
    assert not source.closed


def test_sevenzip_candidate_dispatches_to_a_reader(tmp_path) -> None:
    path = write_7z(tmp_path / "data.7z", [ArchiveMember("data", b"payload")])
    reader = open_backend(SourceFormat.SEVEN_ZIP, open_source(path))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == b"payload"
    reader.close()


def test_invalid_internal_format_is_rejected() -> None:
    with pytest.raises(TypeError, match="SourceFormat"):
        open_backend("plain", open_source(io.BytesIO(b"payload")))


def test_backend_package_has_no_eager_concrete_exports() -> None:
    assert "PlainBackendReader" not in vars(backend_package)
    assert "open_plain_backend" not in vars(backend_package)
