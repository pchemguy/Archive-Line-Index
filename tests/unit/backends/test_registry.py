"""Tests for MVP backend dispatch."""

import io

import pytest

import archive_line_index.backends as backend_package
from archive_line_index.backends.base import BackendReader
from archive_line_index.backends.registry import open_backend
from archive_line_index.errors import UnsupportedFormatError
from archive_line_index.formats import SourceFormat
from archive_line_index.sources import open_source


def test_plain_candidate_dispatches_to_a_reader() -> None:
    reader = open_backend(SourceFormat.PLAIN, open_source(io.BytesIO(b"payload")))
    assert isinstance(reader, BackendReader)
    assert reader.read(16) == b"payload"


@pytest.mark.parametrize(
    "source_format",
    [SourceFormat.ZIP, SourceFormat.TAR, SourceFormat.SEVEN_ZIP],
)
def test_archive_candidates_are_explicitly_unsupported_in_mvp(
    source_format: SourceFormat,
) -> None:
    source = open_source(io.BytesIO(b"candidate"))
    with pytest.raises(UnsupportedFormatError, match=source_format.value):
        open_backend(source_format, source)
    source.close()


def test_invalid_internal_format_is_rejected() -> None:
    with pytest.raises(TypeError, match="SourceFormat"):
        open_backend("plain", open_source(io.BytesIO(b"payload")))


def test_backend_package_has_no_eager_concrete_exports() -> None:
    assert "PlainBackendReader" not in vars(backend_package)
    assert "open_plain_backend" not in vars(backend_package)
