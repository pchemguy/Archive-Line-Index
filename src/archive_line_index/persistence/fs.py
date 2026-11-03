"""Owned temporary siblings and publication primitives with distinct commit points."""

import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def temporary_sibling(destination: Path) -> Iterator[Path]:
    """Yield a unique closed temporary path, removing its owned name on exit.

    Cleanup preserves an existing primary exception with an added note. A lone
    cleanup failure is raised. The context does not own any published destination.
    """
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(name)
    primary: BaseException | None = None
    try:
        os.close(descriptor)
        yield temporary
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except BaseException as cleanup:
            if primary is None:
                raise
            primary.add_note(f"Temporary cleanup failed for {temporary}: {cleanup!r}")


def publish_index_file(temporary: Path, destination: Path, *, overwrite: bool) -> None:
    """Publish a completed file without performing post-commit cleanup.

    Exclusive hard-link creation cannot replace an existing name, even a dangling
    symlink. Unsupported exclusive creation raises without an overwriting fallback.
    Explicit overwrite uses same-filesystem atomic replacement.
    """
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a bool")
    if overwrite:
        os.replace(temporary, destination)
    else:
        os.link(temporary, destination)
