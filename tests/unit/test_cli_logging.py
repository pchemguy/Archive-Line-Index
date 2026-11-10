"""CLI logging is scoped, suppressible and respectful of application handlers."""

import io
import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import Mock

import pytest

from archive_stream import cli, scanner

LOGGER = "archive_stream.scanner"


@pytest.fixture
def isolated_logger() -> Iterator[logging.Logger]:
    logger = logging.getLogger(LOGGER)
    old = logger.level, logger.handlers, logger.propagate, logger.disabled
    logger.handlers = []
    logger.propagate = True
    logger.disabled = False
    logger.setLevel(logging.ERROR)
    try:
        yield logger
    finally:
        logger.handlers, logger.propagate, logger.disabled = old[1:]
        logger.setLevel(old[0])


def target(tmp_path: Path) -> Path:
    source = tmp_path / "payload.txt"
    source.write_bytes(b"a\nb")
    return source


@pytest.mark.parametrize(
    "level,visible",
    [
        (None, True),
        ("info", True),
        ("DEBUG", True),
        ("WARNING", False),
        ("ERROR", False),
        ("CRITICAL", False),
    ],
)
def test_default_and_selected_cli_progress(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    isolated_logger: logging.Logger,
    level: str | None,
    visible: bool,
) -> None:
    isolated_logger.propagate = False
    source = target(tmp_path)
    args = [str(source)] if level is None else ["--log-level", level, str(source)]
    assert cli.main(args) == 0
    out, err = capsys.readouterr()
    assert out.startswith("Indexed 2 lines:")
    assert ("Scan complete: 3 uncompressed bytes" in err) == visible
    assert isolated_logger.level == logging.ERROR and not isolated_logger.handlers


def test_warning_suppresses_preconfigured_info_child(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    isolated_logger: logging.Logger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    isolated_logger.propagate = False
    isolated_logger.setLevel(logging.INFO)
    clock = Mock(side_effect=AssertionError("suppressed progress checked the clock"))
    monkeypatch.setattr(scanner, "monotonic", clock)
    assert cli.main([str(target(tmp_path)), "--log-level", "WARNING"]) == 0
    assert not capsys.readouterr().err and clock.call_count == 0
    assert isolated_logger.level == logging.INFO and not isolated_logger.handlers


def test_repeated_calls_do_not_accumulate_handlers(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    isolated_logger: logging.Logger,
) -> None:
    isolated_logger.propagate = False
    source = target(tmp_path)
    for _ in range(3):
        assert cli.main([str(source), "--overwrite"]) == 0
        assert capsys.readouterr().err.count("Scan complete:") == 1
        assert isolated_logger.level == logging.ERROR and not isolated_logger.handlers


def test_existing_handler_and_formatter_remain_application_owned(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    isolated_logger: logging.Logger,
) -> None:
    isolated_logger.propagate = False
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    formatter = logging.Formatter("CUSTOM %(message)s")
    handler.setFormatter(formatter)
    isolated_logger.addHandler(handler)
    isolated_logger.setLevel(logging.WARNING)
    root = logging.getLogger()
    before = root.level, root.handlers[:], root.propagate, root.disabled
    assert cli.main([str(target(tmp_path))]) == 0
    assert not capsys.readouterr().err
    assert buffer.getvalue().count("CUSTOM Scan complete: 3 uncompressed bytes") == 1
    assert isolated_logger.handlers == [handler] and handler.formatter is formatter
    assert isolated_logger.level == logging.WARNING and not buffer.closed
    assert (root.level, root.handlers, root.propagate, root.disabled) == before
    isolated_logger.warning("application still owns this")
    assert "application still owns this" in buffer.getvalue()
    isolated_logger.removeHandler(handler)
    handler.close()


def test_effective_root_handlers_are_reused(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    isolated_logger: logging.Logger,
) -> None:
    isolated_logger.propagate = False
    isolated_logger.propagate = True
    root = logging.getLogger()
    before = root.level, root.handlers[:]
    assert cli.main([str(target(tmp_path))]) == 0
    records = [r for r in caplog.records if r.name == LOGGER]
    assert sum(r.getMessage().startswith("Scan complete:") for r in records) == 1
    assert not isolated_logger.handlers and isolated_logger.level == logging.ERROR
    assert (root.level, root.handlers) == before


@pytest.mark.parametrize(
    "error,status",
    [
        (OSError("source"), 1),
        (MemoryError(), 1),
        (KeyboardInterrupt(), 130),
        (RuntimeError("programming"), None),
    ],
    ids=["source", "memory", "interrupt", "unexpected"],
)
def test_logging_state_restored_on_every_scan_failure(
    tmp_path: Path,
    isolated_logger: logging.Logger,
    monkeypatch: pytest.MonkeyPatch,
    error: BaseException,
    status: int | None,
) -> None:
    isolated_logger.propagate = False

    def fail(*args: object, **kwargs: object) -> None:
        assert isolated_logger.level == logging.INFO
        assert len(isolated_logger.handlers) == 1
        raise error

    monkeypatch.setattr(cli, "build_line_index", fail)
    args = [str(target(tmp_path))]
    if status is None:
        with pytest.raises(RuntimeError, match="programming"):
            cli.main(args)
    else:
        assert cli.main(args) == status
    assert isolated_logger.level == logging.ERROR and not isolated_logger.handlers


@pytest.mark.parametrize(
    "argv,status", [(["--help"], 0), (["--log-level", "WRONG", "absent"], 2)]
)
def test_help_and_usage_do_not_configure_logging(
    monkeypatch: pytest.MonkeyPatch,
    isolated_logger: logging.Logger,
    argv: list[str],
    status: int,
) -> None:
    isolated_logger.propagate = False
    setup = Mock(side_effect=AssertionError("configured logging"))
    monkeypatch.setattr(cli, "_progress_logging", setup, raising=False)
    assert cli.main(argv) == status
    assert not setup.called and isolated_logger.level == logging.ERROR


def test_handler_setup_failure_restores_level_before_source_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_logger: logging.Logger,
) -> None:
    isolated_logger.propagate = False
    build = Mock(side_effect=AssertionError("source opened before handler ready"))
    monkeypatch.setattr(cli, "build_line_index", build)
    monkeypatch.setattr(logging, "StreamHandler", Mock(side_effect=MemoryError()))
    assert cli.main([str(target(tmp_path))]) == 1
    assert not build.called
    assert isolated_logger.level == logging.ERROR and not isolated_logger.handlers
