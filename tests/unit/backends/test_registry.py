"""Tests for path-based backend dispatch."""

import pytest

import archive_line_index.backends as backend_package
from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.registry import open_backend
from archive_line_index.formats import SourceFormat
from tests.helpers.archive_factory import ArchiveMember, write_7z, write_tar, write_zip


@pytest.mark.parametrize("source_format", list(SourceFormat))
def test_candidate_dispatches_to_a_reader(tmp_path, source_format) -> None:
    content = b"payload"
    if source_format is SourceFormat.PLAIN:
        path = tmp_path / "data"
        path.write_bytes(content)
    elif source_format is SourceFormat.ZIP:
        path = write_zip(tmp_path / "data.zip", [ArchiveMember("data", content)])
    elif source_format is SourceFormat.TAR:
        path = write_tar(tmp_path / "data.tar", [ArchiveMember("data", content)])
    else:
        path = write_7z(tmp_path / "data.7z", [ArchiveMember("data", content)])

    reader = open_backend(source_format, str(path))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == content
    reader.close()


def test_invalid_internal_format_is_rejected(tmp_path) -> None:
    path = tmp_path / "data"
    path.write_bytes(b"payload")
    with pytest.raises(TypeError, match="SourceFormat"):
        open_backend("plain", str(path))


def test_backend_package_has_no_eager_concrete_exports() -> None:
    assert "PlainBackendReader" not in vars(backend_package)
    assert "open_plain_backend" not in vars(backend_package)
