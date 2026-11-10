"""Delivered package-root exports are explicit and independent of future adapters."""

import pytest

import archive_stream as ali


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


def test_version_and_console_metadata() -> None:
    import re
    import tomllib
    from pathlib import Path

    project = tomllib.loads(
        (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )["project"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", project["version"])
    assert project["scripts"] == {"archive-line-index": "archive_stream.cli:main"}


def test_imports_have_no_cli_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse
    import importlib
    import sys
    from pathlib import Path
    from unittest.mock import patch

    import archive_stream.cli as cli

    class UnreadableArgv:
        def __getitem__(self, key: object) -> object:
            raise AssertionError("argv read during import")

    monkeypatch.setattr(sys, "argv", UnreadableArgv())
    with (
        patch.object(
            argparse.ArgumentParser, "parse_args", side_effect=AssertionError("parsed")
        ),
        patch.object(Path, "open", side_effect=AssertionError("opened")),
        patch.object(Path, "stat", side_effect=AssertionError("inspected")),
        patch("builtins.print", side_effect=AssertionError("printed")),
    ):
        importlib.reload(ali)
        importlib.reload(cli)
        importlib.import_module("archive_stream.__main__")


def test_module_runner_converts_main_status_to_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import runpy
    import sys
    from unittest.mock import patch

    monkeypatch.delitem(sys.modules, "archive_stream.__main__", raising=False)
    with (
        patch("archive_stream.cli.main", return_value=17) as main,
        pytest.raises(SystemExit) as caught,
    ):
        runpy.run_module("archive_stream", run_name="__main__")
    assert caught.value.code == 17
    main.assert_called_once_with()
