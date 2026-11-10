"""Real independent writers retain complete-file publication guarantees."""

from array import array
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_stream.persistence import raw, sqlite
from archive_stream.persistence.fs import publish_index_file


@pytest.mark.parametrize("kind", ["raw", "sqlite"])
def test_writer_commit_time_race_preserves_other_actor_file(
    tmp_path: Path, kind: str
) -> None:
    module = raw if kind == "raw" else sqlite
    writer = raw.write_raw_index if kind == "raw" else sqlite.write_sqlite_index
    destination = tmp_path / "output"

    def raced(temporary: Path, target: Path, *, overwrite: bool) -> None:
        target.write_bytes(b"concurrent actor")
        publish_index_file(temporary, target, overwrite=overwrite)

    with (
        patch.object(module, "publish_index_file", raced),
        pytest.raises(FileExistsError),
    ):
        writer(array("Q", [0, 5]), destination)
    assert destination.read_bytes() == b"concurrent actor"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize("kind", ["raw", "sqlite"])
def test_writer_flush_failure_preserves_previous_destination(
    tmp_path: Path, kind: str
) -> None:
    module = raw if kind == "raw" else sqlite
    writer = raw.write_raw_index if kind == "raw" else sqlite.write_sqlite_index
    destination = tmp_path / "output"
    destination.write_bytes(b"previous")
    with (
        patch.object(module, "flush_file", side_effect=OSError("flush fault")),
        pytest.raises(OSError, match="flush fault"),
    ):
        writer(array("Q", [0, 5]), destination, overwrite=True)
    assert destination.read_bytes() == b"previous"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize("kind", ["raw", "sqlite"])
def test_writer_rejects_dangling_destination_before_allocation(
    tmp_path: Path, kind: str
) -> None:
    module = raw if kind == "raw" else sqlite
    writer = raw.write_raw_index if kind == "raw" else sqlite.write_sqlite_index
    destination = tmp_path / "output"
    try:
        destination.symlink_to(tmp_path / "missing")
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with (
        patch.object(
            module, "temporary_sibling", side_effect=AssertionError("allocated")
        ),
        pytest.raises(FileExistsError),
    ):
        writer(array("Q", [0]), destination)
    assert destination.is_symlink()
