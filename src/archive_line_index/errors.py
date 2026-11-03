"""Public domain errors shared by streaming, indexing and persistence."""


class ArchiveLineIndexError(Exception):
    """Base class for package-domain failures."""


class UnsupportedFormatError(ArchiveLineIndexError):
    """The source format is unsupported by the delivered implementation."""


class InvalidArchiveError(ArchiveLineIndexError):
    """An archive cannot be parsed or validated."""


class ArchiveStructureError(ArchiveLineIndexError):
    """Archive members violate the single-payload policy."""


class SizeLimitExceededError(ArchiveLineIndexError):
    """The payload exceeds its inclusive byte limit."""


class ExtractionError(ArchiveLineIndexError):
    """Payload delivery or terminal validation failed."""


class InvalidIndexError(ArchiveLineIndexError):
    """Offsets violate the canonical index representation."""


class PersistenceError(ArchiveLineIndexError):
    """Index storage, loading or publication failed."""
