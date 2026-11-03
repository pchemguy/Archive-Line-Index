"""Importable single-target CLI orchestration, parsing and output/status contracts."""

from array import array
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_line_index.cli import main


@pytest.mark.parametrize(
    "offsets", [array("Q", [0]), array("Q", [3]), array("Q", [0, 2, 5])]
)
def test_one_scan_same_array_sqlite_then_raw(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], offsets: array
) -> None:
    target = tmp_path / "payload.txt"
    events: list[str] = []
    with (
        patch("archive_line_index.cli.build_line_index", return_value=offsets) as build,
        patch(
            "archive_line_index.cli.write_sqlite_index",
            side_effect=lambda *a, **k: events.append("sqlite"),
        ) as sqlite,
        patch(
            "archive_line_index.cli.write_raw_index",
            side_effect=lambda *a, **k: events.append("raw"),
        ) as raw,
    ):
        assert main([str(target)]) == 0
    build.assert_called_once_with(target)
    sqlite.assert_called_once_with(
        offsets, tmp_path / "payload.sqlite3", overwrite=False
    )
    raw.assert_called_once_with(offsets, tmp_path / "payload.u64", overwrite=False)
    assert sqlite.call_args.args[0] is raw.call_args.args[0] is offsets
    assert events == ["sqlite", "raw"]
    out, err = capsys.readouterr()
    assert (
        str(tmp_path / "payload.sqlite3") in out
        and str(tmp_path / "payload.u64") in out
    )
    assert str(len(offsets) - 1) in out and not err


@pytest.mark.parametrize(
    "argv,status",
    [(["--help"], 0), ([], 2), (["a", "b"], 2), (["--unknown"], 2), (["--output"], 2)],
)
def test_help_usage_return_without_io(
    argv: list[str], status: int, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch.object(Path, "stat", side_effect=AssertionError("path inspected")),
        patch(
            "archive_line_index.cli.build_line_index",
            side_effect=AssertionError("indexed"),
        ),
    ):
        assert main(argv) == status
    out, err = capsys.readouterr()
    assert "usage:" in (out if status == 0 else err)
    assert not (err if status == 0 else out)


@pytest.mark.parametrize("argv", ["payload.txt", b"payload", {"x": "y"}, [1], [b"x"]])
def test_invalid_python_argv_raises_type_error(argv: object) -> None:
    with pytest.raises(TypeError):
        main(argv)  # type: ignore[arg-type]


def test_none_argv_uses_process_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["program", "--help"])
    assert main() == 0
