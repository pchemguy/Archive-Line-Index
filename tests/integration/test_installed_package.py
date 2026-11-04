"""Public workflows from actual wheel bytes and a source-rebuilt wheel."""

import pytest
from tests.helpers.packaging import InstalledPackage

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_installed_plain_workflows_and_runtime_boundary(
    installed_package: InstalledPackage,
) -> None:
    assert (
        installed_package.run("""
import importlib.metadata as metadata
import io
from pathlib import Path
import sys
import archive_line_index as ali

assert Path(ali.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert metadata.version("archive-line-index") == "0.4.0"
assert metadata.version("py7zr")
names = {d.metadata["Name"].lower() for d in metadata.distributions()}
assert not names.intersection({"pytest", "mypy", "ruff", "build", "hatchling", "flowmark"})
assert not any(k == "py7zr" or k.startswith("archive_line_index.backends.zip") or k.startswith("archive_line_index.backends.sevenzip") for k in sys.modules)
expected = {"read_raw_index", "write_raw_index", "read_sqlite_index", "write_sqlite_index", "Source", "ReadableBinary", "DEFAULT_BUFFER_SIZE", "ContentStream", "open_content_stream", "scan_line_offsets", "build_line_index", "ArchiveLineIndexError", "UnsupportedFormatError", "InvalidArchiveError", "ArchiveStructureError", "SizeLimitExceededError", "ExtractionError", "InvalidIndexError", "PersistenceError"}
assert set(ali.__all__) == expected
payload = b"\\xef\\xbb\\xbfabc\\r\\n\\nlast"
path = Path("payload.bin")
path.write_bytes(payload)
with ali.open_content_stream(path) as stream:
    assert stream.read(2) + stream.read() == payload
assert stream.closed
borrowed = io.BytesIO(payload)
assert ali.scan_line_offsets(borrowed, buffer_size=1).tolist() == [3, 8, 9, 13]
assert not borrowed.closed
assert ali.build_line_index(path, buffer_size=2).tolist() == [3, 8, 9, 13]
try:
    ali.build_line_index(path, max_uncompressed_size=12)
except ali.SizeLimitExceededError:
    pass
else:
    raise AssertionError("limit ignored")
path.unlink()
from array import array
values = array("Q", [0, 2, 7])
ali.write_sqlite_index(values, "standalone.sqlite3")
ali.write_raw_index(values, "standalone.u64")
assert ali.read_sqlite_index("standalone.sqlite3") == ali.read_raw_index("standalone.u64") == values
Path("standalone.sqlite3").unlink()
Path("standalone.u64").unlink()
print("installed workflows passed")
""").strip()
        == "installed workflows passed"
    )
