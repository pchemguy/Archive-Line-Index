"""Check the stable domain-error boundary."""

import archive_line_index as ali
from archive_line_index import errors


def test_domain_error_hierarchy_and_identity() -> None:
    names = (
        "UnsupportedFormatError",
        "InvalidArchiveError",
        "ArchiveStructureError",
        "SizeLimitExceededError",
        "ExtractionError",
        "InvalidIndexError",
        "PersistenceError",
    )
    for name in names:
        kind = getattr(errors, name)
        assert issubclass(kind, errors.ArchiveLineIndexError)
        assert getattr(ali, name) is kind
        assert str(kind("detail")) == "detail"
