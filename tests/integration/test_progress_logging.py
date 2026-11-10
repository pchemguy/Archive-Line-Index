"""Real formats and installed routes retain byte/index semantics with progress."""

import io
import logging
import tarfile
import zipfile
from pathlib import Path

import pytest
from tests.helpers.archives import make_tar
from tests.helpers.packaging import InstalledPackage
from tests.helpers.sevenzip import make_7z
from tests.integration.test_installed_cli import _assert_progress_success, _invoke

from archive_stream import build_line_index, open_content_stream, scan_line_offsets

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]
PAYLOAD = b"\xef\xbb\xbfalpha\r\n\nomega"


@pytest.mark.parametrize("kind", ["plain", "zip", "tar", "gz", "bz2", "xz", "7z"])
def test_actual_formats_report_payload_bytes_without_duplicate_stream_logging(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, kind: str
) -> None:
    source = tmp_path / ("payload." + kind)
    if kind == "plain":
        source.write_bytes(PAYLOAD)
    elif kind == "zip":
        with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("nested/data", PAYLOAD)
    elif kind == "7z":
        make_7z(source, [("nested/data", PAYLOAD)])
    else:
        make_tar(
            source,
            [("nested/data", PAYLOAD, tarfile.REGTYPE)],
            mode={"tar": "w", "gz": "w:gz", "bz2": "w:bz2", "xz": "w:xz"}[kind],
        )
    with caplog.at_level(logging.INFO, logger="archive_stream.scanner"):
        assert build_line_index(source, buffer_size=2).tolist() == [3, 10, 11, 16]
        records = [r for r in caplog.records if r.name == "archive_stream.scanner"]
        assert records[-2].getMessage() == "Scan complete: 16 uncompressed bytes"
        assert records[-1].getMessage().startswith("Scan time: ")
        caplog.clear()
        with open_content_stream(source) as stream:
            assert stream.read() == PAYLOAD
        assert not [r for r in caplog.records if r.name == "archive_stream.scanner"]
        assert scan_line_offsets(io.BytesIO(PAYLOAD)).tolist() == [3, 10, 11, 16]
        assert [r for r in caplog.records if r.name == "archive_stream.scanner"][
            -2
        ].args == (16,)


@pytest.mark.parametrize("route", ["console", "module", "imported"])
def test_installed_default_progress_suppression_and_invalid_level(
    installed_package: InstalledPackage, route: str
) -> None:
    source = installed_package.workdir / ("progress-" + route + ".txt")
    source.write_bytes(PAYLOAD)
    result = _invoke(installed_package, route, [source.name])
    _assert_progress_success(result, 16)
    quiet = _invoke(
        installed_package, route, ["--overwrite", "--log-level", "warning", source.name]
    )
    assert quiet.returncode == 0 and not quiet.stderr, quiet.stderr
    invalid = _invoke(installed_package, route, ["--log-level", "INVALID", source.name])
    assert invalid.returncode == 2 and "usage:" in invalid.stderr and not invalid.stdout
    installed_package.run(f"""
import logging
root = logging.getLogger()
before = root.level, root.handlers[:]
from archive_stream import read_raw_index, read_sqlite_index
assert (root.level, root.handlers) == before
assert read_raw_index({str(source.with_suffix(".u64"))!r}).tolist() == [3, 10, 11, 16]
assert read_sqlite_index({str(source.with_suffix(".sqlite3"))!r}).tolist() == [3, 10, 11, 16]
from archive_stream.cli import main
assert (root.level, root.handlers) == before
logger = logging.getLogger("archive_stream.scanner")
previous = logger.level, logger.handlers[:], logger.propagate
assert main(["--overwrite", "--log-level", "WARNING", {str(source)!r}]) == 0
assert (logger.level, logger.handlers, logger.propagate) == previous
assert (root.level, root.handlers) == before
""")
