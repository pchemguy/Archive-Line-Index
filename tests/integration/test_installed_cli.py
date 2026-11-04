"""Console/module/imported commands run against real installed native artifacts."""

from __future__ import annotations

import os
import subprocess

import pytest
from tests.helpers.packaging import InstalledPackage

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def _invoke(
    package: InstalledPackage, route: str, argv: list[str], *, code: str | None = None
) -> subprocess.CompletedProcess[str]:
    if route == "console":
        command = [
            str(
                package.python.parent
                / (
                    "archive-line-index.exe"
                    if os.name == "nt"
                    else "archive-line-index"
                )
            )
        ]
    elif route == "module":
        command = [str(package.python), "-I", "-m", "archive_line_index"]
    else:
        command = [
            str(package.python),
            "-I",
            "-c",
            code or "from archive_line_index.cli import main; raise SystemExit(main())",
        ]
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    return subprocess.run(
        command + argv,
        cwd=package.workdir,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _assert_progress_success(
    result: subprocess.CompletedProcess[str], byte_count: int
) -> None:
    """Retain success/diagnostic checks while accepting informational progress."""
    assert result.returncode == 0, result.stderr
    lines = result.stderr.splitlines()
    assert (
        lines and lines[-1] == f"INFO: Scan complete: {byte_count} uncompressed bytes"
    )
    assert sum("Scan complete:" in line for line in lines) == 1
    assert all(line.startswith("INFO: Scanned ") or line == lines[-1] for line in lines)


@pytest.mark.parametrize("route", ["console", "module", "imported"])
def test_installed_forms_default_explicit_and_overwrite(
    installed_package: InstalledPackage, route: str
) -> None:
    source = installed_package.workdir / ("-payload " + route + ".txt")
    source.write_bytes(b"\xef\xbb\xbfabc\r\n\nlast")
    argv = ["--", source.name]
    result = _invoke(installed_package, route, argv)
    _assert_progress_success(result, 13)
    assert (
        ".sqlite3" in result.stdout
        and ".u64" in result.stdout
        and "3 lines" in result.stdout
    )
    stem = source.stem
    installed_package.run(f"""
from archive_line_index import read_sqlite_index, read_raw_index
assert read_sqlite_index({stem + ".sqlite3"!r}).tolist() == [3, 8, 9, 13]
assert read_raw_index({stem + ".u64"!r}).tolist() == [3, 8, 9, 13]
""")
    before = {
        suffix: (source.with_suffix(suffix)).read_bytes()
        for suffix in (".sqlite3", ".u64")
    }
    protected = _invoke(installed_package, route, argv)
    assert protected.returncode == 1 and not protected.stdout and protected.stderr
    assert all(source.with_suffix(s).read_bytes() == data for s, data in before.items())
    replaced = _invoke(installed_package, route, ["--overwrite", "--", source.name])
    _assert_progress_success(replaced, 13)
    explicit = _invoke(
        installed_package, route, ["-o", "explicit." + route, "--", source.name]
    )
    _assert_progress_success(explicit, 13)
    assert (installed_package.workdir / ("explicit." + route + ".sqlite3")).is_file()
    assert (installed_package.workdir / ("explicit." + route + ".u64")).is_file()


def test_installed_help_usage_and_real_missing_parent(
    installed_package: InstalledPackage,
) -> None:
    help_result = _invoke(installed_package, "console", ["--help"])
    assert (
        help_result.returncode == 0
        and "usage:" in help_result.stdout
        and not help_result.stderr
    )
    usage = _invoke(installed_package, "module", [])
    assert usage.returncode == 2 and not usage.stdout and "usage:" in usage.stderr
    source = installed_package.workdir / "missing-parent.txt"
    source.write_bytes(b"abc")
    failed = _invoke(
        installed_package, "console", [str(source), "-o", "nonexistent/output"]
    )
    assert failed.returncode == 1 and not failed.stdout and failed.stderr
    assert not (installed_package.workdir / "nonexistent").exists()


@pytest.mark.parametrize("interrupt", [False, True])
def test_installed_partial_failure_and_signal_cleanup(
    installed_package: InstalledPackage, interrupt: bool
) -> None:
    name = "signal" if interrupt else "failure"
    source = installed_package.workdir / (name + ".txt")
    source.write_bytes(b"abc")
    effect = (
        "lambda *args: signal.raise_signal(signal.SIGINT)"
        if interrupt
        else 'OSError("raw failure")'
    )
    code = f"""
import signal
from unittest.mock import patch
from archive_line_index.cli import main
with patch("archive_line_index.persistence.raw._write_all", side_effect={effect}):
    raise SystemExit(main())
"""
    result = _invoke(installed_package, "imported", [source.name], code=code)
    assert result.returncode == (130 if interrupt else 1), result.stderr
    assert (
        not result.stdout
        and "Already published" in result.stderr
        and name + ".sqlite3" in result.stderr
    )
    assert not (installed_package.workdir / (name + ".u64")).exists()
    assert not list(installed_package.workdir.glob("." + name + ".*.tmp"))
    installed_package.run(f"""
from archive_line_index import read_sqlite_index
assert read_sqlite_index({name + ".sqlite3"!r}).tolist() == [0, 3]
""")
