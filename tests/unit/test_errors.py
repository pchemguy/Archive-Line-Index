"""Tests for the public exception hierarchy."""

import archive_line_index.errors as errors


PUBLIC_ERROR_NAMES = (
    "ArchiveLineIndexError",
    "UnsupportedFormatError",
    "InvalidArchiveError",
    "ArchiveStructureError",
    "EncryptedArchiveError",
    "SizeLimitExceededError",
    "ExtractionError",
    "InvalidIndexError",
    "PersistenceError",
)


def test_public_error_names_are_stable() -> None:
    for name in PUBLIC_ERROR_NAMES:
        error_type = getattr(errors, name)
        assert error_type.__name__ == name


def test_package_errors_share_one_base_class() -> None:
    for name in PUBLIC_ERROR_NAMES[1:]:
        error_type = getattr(errors, name)
        assert error_type.__bases__ == (errors.ArchiveLineIndexError,)
        assert issubclass(error_type, Exception)


def test_ordinary_errors_are_not_redefined() -> None:
    for name in (
        "FileNotFoundError",
        "FileExistsError",
        "PermissionError",
        "TypeError",
        "ValueError",
        "MemoryError",
    ):
        assert name not in vars(errors)
