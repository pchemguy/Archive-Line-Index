"""Exclusive publication, explicit replacement and owned temporary cleanup."""

import errno
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_stream.persistence.fs import publish_index_file, temporary_sibling


def test_exclusive_publish_leaves_cleanup_to_outer_owner(tmp_path: Path) -> None:
    destination = tmp_path / "result"
    with temporary_sibling(destination) as temporary:
        assert temporary.parent == destination.parent and temporary != destination
        temporary.write_bytes(b"complete")
        publish_index_file(temporary, destination, overwrite=False)
        assert temporary.exists() and destination.read_bytes() == b"complete"
    assert not temporary.exists()
    assert destination.read_bytes() == b"complete"


@pytest.mark.parametrize("overwrite", [False, True])
def test_existing_destination_or_authorized_replacement(
    tmp_path: Path, overwrite: bool
) -> None:
    destination = tmp_path / "result"
    destination.write_bytes(b"previous")
    with temporary_sibling(destination) as temporary:
        temporary.write_bytes(b"new")
        if overwrite:
            publish_index_file(temporary, destination, overwrite=True)
            assert destination.read_bytes() == b"new"
        else:
            with pytest.raises(FileExistsError):
                publish_index_file(temporary, destination, overwrite=False)
            assert destination.read_bytes() == b"previous"
    assert not temporary.exists()


def test_dangling_symlink_is_protected(tmp_path: Path) -> None:
    destination = tmp_path / "result"
    try:
        destination.symlink_to(tmp_path / "missing")
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with temporary_sibling(destination) as temporary:
        with pytest.raises(FileExistsError):
            publish_index_file(temporary, destination, overwrite=False)
    assert destination.is_symlink()


def test_commit_time_race_and_unsupported_primitive_do_not_replace(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "result"
    with temporary_sibling(destination) as temporary:
        temporary.write_bytes(b"complete")
        destination.write_bytes(b"concurrent")
        with pytest.raises(FileExistsError):
            publish_index_file(temporary, destination, overwrite=False)
    with temporary_sibling(destination) as temporary:
        with (
            patch(
                "archive_stream.persistence.fs.os.link",
                side_effect=OSError(errno.ENOTSUP, "unavailable"),
            ),
            patch(
                "archive_stream.persistence.fs.os.replace",
                side_effect=AssertionError("unsafe fallback"),
            ),
        ):
            with pytest.raises(OSError, match="unavailable"):
                publish_index_file(temporary, destination, overwrite=False)
    assert destination.read_bytes() == b"concurrent"


def test_cleanup_failure_preserves_primary_and_reports_standalone_failure(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "result"
    error = RuntimeError("build fault")
    with patch.object(Path, "unlink", side_effect=PermissionError("cleanup fault")):
        with pytest.raises(RuntimeError) as caught:
            with temporary_sibling(destination) as temporary:
                raise error
    assert caught.value is error and "cleanup fault" in error.__notes__[0]
    temporary.unlink()
    with patch.object(Path, "unlink", side_effect=PermissionError("cleanup fault")):
        with pytest.raises(PermissionError, match="cleanup fault"):
            with temporary_sibling(destination) as temporary:
                pass
    temporary.unlink()
    assert not destination.exists()
