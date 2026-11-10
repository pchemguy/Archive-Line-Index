"""Importable single-target CLI orchestration, parsing and output/status contracts."""

from array import array
from pathlib import Path
from unittest.mock import patch

import pytest

from archive_stream.cli import main
from archive_stream.errors import ExtractionError


@pytest.mark.parametrize(
    "offsets", [array("Q", [0]), array("Q", [3]), array("Q", [0, 2, 5])]
)
def test_one_scan_same_array_sqlite_then_raw(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], offsets: array
) -> None:
    target = tmp_path / "payload.txt"
    events: list[str] = []
    with (
        patch("archive_stream.cli.build_line_index", return_value=offsets) as build,
        patch(
            "archive_stream.cli.write_sqlite_index",
            side_effect=lambda *a, **k: events.append("sqlite"),
        ) as sqlite,
        patch(
            "archive_stream.cli.write_raw_index",
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
            "archive_stream.cli.build_line_index",
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


@pytest.mark.parametrize(
    "name,stem",
    [
        ("events.tar.gz", "events.tar"),
        ("events", "events"),
        (".hidden", ".hidden"),
        ("name with spaces.txt", "name with spaces"),
        ("events.zip", "events"),
    ],
)
def test_default_final_suffix_stems(tmp_path: Path, name: str, stem: str) -> None:
    with (
        patch("archive_stream.cli.build_line_index", return_value=array("Q", [0])),
        patch("archive_stream.cli.write_sqlite_index") as sqlite,
        patch("archive_stream.cli.write_raw_index") as raw,
    ):
        assert main([str(tmp_path / name)]) == 0
    assert sqlite.call_args.args[1] == tmp_path / (stem + ".sqlite3")
    assert raw.call_args.args[1] == tmp_path / (stem + ".u64")


def test_explicit_stem_is_appended_and_hyphen_target_after_separator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with (
        patch(
            "archive_stream.cli.build_line_index", return_value=array("Q", [0])
        ) as build,
        patch("archive_stream.cli.write_sqlite_index") as sqlite,
        patch("archive_stream.cli.write_raw_index") as raw,
    ):
        assert main(["-o", "results/custom.v1", "--", "-payload.txt"]) == 0
    build.assert_called_once_with(Path("-payload.txt"))
    assert sqlite.call_args.args[1] == Path("results/custom.v1.sqlite3")
    assert raw.call_args.args[1] == Path("results/custom.v1.u64")
    assert not (tmp_path / "results").exists()


@pytest.mark.parametrize("suffix", [".sqlite3", ".u64"])
def test_either_existing_output_blocks_before_scan(
    tmp_path: Path, suffix: str, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / ("payload" + suffix)
    output.write_bytes(b"protected")
    with patch(
        "archive_stream.cli.build_line_index", side_effect=AssertionError("scanned")
    ):
        assert main([str(tmp_path / "payload.txt")]) == 1
    out, err = capsys.readouterr()
    assert not out and str(output) in err
    assert output.read_bytes() == b"protected"


@pytest.mark.parametrize("suffix", [".sqlite3", ".u64"])
def test_default_source_collision_rejected_even_overwrite(
    tmp_path: Path, suffix: str
) -> None:
    source = tmp_path / ("payload" + suffix)
    source.write_bytes(b"source")
    with patch(
        "archive_stream.cli.build_line_index", side_effect=AssertionError("scanned")
    ):
        assert main([str(source), "--overwrite"]) == 1
    assert source.read_bytes() == b"source"


@pytest.mark.parametrize("kind", ["hardlink", "symlink", "dangling"])
def test_output_alias_and_dangling_protection(tmp_path: Path, kind: str) -> None:
    import os

    source = tmp_path / "payload.txt"
    source.write_bytes(b"source")
    output = tmp_path / "payload.u64"
    try:
        if kind == "hardlink":
            os.link(source, output)
        else:
            output.symlink_to(source if kind == "symlink" else tmp_path / "missing")
    except (OSError, NotImplementedError):
        pytest.skip("link creation unavailable")
    with patch(
        "archive_stream.cli.build_line_index", side_effect=AssertionError("scanned")
    ):
        argv = [str(source)] + ([] if kind == "dangling" else ["--overwrite"])
        assert main(argv) == 1
    assert source.read_bytes() == b"source"


def test_explicit_overwrite_allows_distinct_outputs(tmp_path: Path) -> None:
    for suffix in (".sqlite3", ".u64"):
        (tmp_path / ("out" + suffix)).write_bytes(b"old")
    with (
        patch("archive_stream.cli.build_line_index", return_value=array("Q", [0])),
        patch("archive_stream.cli.write_sqlite_index") as sqlite,
        patch("archive_stream.cli.write_raw_index") as raw,
    ):
        assert (
            main(
                [
                    str(tmp_path / "input.txt"),
                    "-o",
                    str(tmp_path / "out"),
                    "--overwrite",
                ]
            )
            == 0
        )
    assert sqlite.call_args.kwargs == raw.call_args.kwargs == {"overwrite": True}


@pytest.mark.parametrize("stage", ["build", "sqlite", "raw"])
@pytest.mark.parametrize("error_kind", [OSError, MemoryError, ExtractionError])
def test_operational_failure_status_and_known_publications(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stage: str,
    error_kind: type[Exception],
) -> None:
    error = error_kind("operational fault")
    values = array("Q", [0, 3])
    with (
        patch(
            "archive_stream.cli.build_line_index",
            side_effect=error if stage == "build" else None,
            return_value=values,
        ),
        patch(
            "archive_stream.cli.write_sqlite_index",
            side_effect=error if stage == "sqlite" else None,
        ) as sqlite,
        patch(
            "archive_stream.cli.write_raw_index",
            side_effect=error if stage == "raw" else None,
        ) as raw,
    ):
        assert main([str(tmp_path / "payload.txt")]) == 1
    out, err = capsys.readouterr()
    assert not out and str(error) in err and "Traceback" not in err
    if stage == "build":
        sqlite.assert_not_called()
    if stage != "raw":
        raw.assert_not_called()
    else:
        assert "Already published" in err and str(tmp_path / "payload.sqlite3") in err


def test_interruption_preserves_known_sqlite_publication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("archive_stream.cli.build_line_index", return_value=array("Q", [0])),
        patch("archive_stream.cli.write_sqlite_index"),
        patch("archive_stream.cli.write_raw_index", side_effect=KeyboardInterrupt),
    ):
        assert main([str(tmp_path / "payload.txt")]) == 130
    out, err = capsys.readouterr()
    assert not out and "Interrupted" in err and str(tmp_path / "payload.sqlite3") in err


def test_unexpected_programming_error_propagates(tmp_path: Path) -> None:
    with (
        patch(
            "archive_stream.cli.build_line_index",
            side_effect=RuntimeError("programming defect"),
        ),
        pytest.raises(RuntimeError, match="programming defect"),
    ):
        main([str(tmp_path / "payload.txt")])


@pytest.mark.parametrize(
    "error,status", [(MemoryError("parser allocation"), 1), (KeyboardInterrupt(), 130)]
)
def test_parser_resource_failure_returns_operational_status(
    error: BaseException, status: int, capsys: pytest.CaptureFixture[str]
) -> None:
    with patch("archive_stream.cli._parser", side_effect=error):
        assert main(["payload.txt"]) == status
    out, err = capsys.readouterr()
    assert not out and err and "Traceback" not in err
