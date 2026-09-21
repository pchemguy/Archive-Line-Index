"""Stable public exceptions raised by :mod:`archive_line_index`."""


class ArchiveLineIndexError(Exception):
    """Base class for package-defined failures."""


class UnsupportedFormatError(ArchiveLineIndexError):
    """The detected archive or compression format is unsupported."""


class InvalidArchiveError(ArchiveLineIndexError):
    """A claimed or detected supported archive is malformed."""


class ArchiveStructureError(ArchiveLineIndexError):
    """Archive entries violate the single-regular-member policy."""


class SizeLimitExceededError(ArchiveLineIndexError):
    """Declared or actual decompressed content exceeds its configured limit."""


class ExtractionError(ArchiveLineIndexError):
    """Archive decompression, integrity validation, or delivery failed."""


class InvalidIndexError(ArchiveLineIndexError):
    """An offset sequence violates the index representation contract."""


class PersistenceError(ArchiveLineIndexError):
    """Index persistence failed without a narrower ordinary exception."""
