"""Delivered package-root exports are explicit and independent of future adapters."""

import archive_line_index as ali


def test_exact_delivered_exports() -> None:
    assert set(ali.__all__) == {
        "read_raw_index",
        "write_raw_index",
        "read_sqlite_index",
        "write_sqlite_index",
        "Source",
        "ReadableBinary",
        "DEFAULT_BUFFER_SIZE",
        "ContentStream",
        "open_content_stream",
        "scan_line_offsets",
        "build_line_index",
        "ArchiveLineIndexError",
        "UnsupportedFormatError",
        "InvalidArchiveError",
        "ArchiveStructureError",
        "SizeLimitExceededError",
        "ExtractionError",
        "InvalidIndexError",
        "PersistenceError",
    }
    for name in ali.__all__:
        assert getattr(ali, name) is not None
