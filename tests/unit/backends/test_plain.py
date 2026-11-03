"""Plain readers own handles and distinguish short data from terminal EOF."""

from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.backends.plain import open_plain_backend


def test_binary_delivery_and_terminal_completion(tmp_path: Path) -> None:
    p = tmp_path / "payload"
    p.write_bytes(b"\0\xff\nABC")
    r = open_plain_backend(p)
    assert r.declared_size == 6
    assert not r.completed
    assert r.read(4) == b"\0\xff\nA"
    assert r.read(4) == b"BC"
    assert not r.completed
    assert r.read(4) == b""
    assert r.completed
    assert r.read(1) == b""
    r.close()
    r.close()
    with pytest.raises(ValueError):
        r.read(1)
    p.unlink()


@pytest.mark.parametrize(
    "size,exc", [(0, ValueError), (-1, ValueError), (True, TypeError), (1.5, TypeError)]
)
def test_invalid_sizes_do_not_advance(
    tmp_path: Path, size: object, exc: type[Exception]
) -> None:
    p = tmp_path / "p"
    p.write_bytes(b"x")
    r = open_plain_backend(p)
    try:
        with pytest.raises(exc):
            r.read(size)  # type: ignore[arg-type]
        assert r.read(1) == b"x"
    finally:
        r.close()


def test_open_metadata_failure_closes_acquired_handle(tmp_path: Path) -> None:
    p = tmp_path / "p"
    p.write_bytes(b"data")
    handle = p.open("rb")
    with (
        patch.object(Path, "open", return_value=handle),
        patch(
            "archive_line_index.backends.plain.os.fstat",
            side_effect=OSError("metadata"),
        ),
    ):
        with pytest.raises(OSError, match="metadata"):
            open_plain_backend(p)
    assert handle.closed
