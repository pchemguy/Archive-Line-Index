"""Archive commands run in clean installed runtimes outside the checkout."""

import zipfile

import pytest
from tests.helpers.packaging import InstalledPackage
from tests.integration.test_installed_cli import _invoke

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


@pytest.mark.parametrize("route", ["console", "module", "imported"])
def test_installed_zip_pairs_and_corruption(
    installed_package: InstalledPackage, route: str
) -> None:
    target = installed_package.workdir / ("archive-" + route + ".zip")
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nested/data", b"\xef\xbb\xbfalpha\r\n\nomega")
    result = _invoke(installed_package, route, [target.name])
    assert result.returncode == 0 and not result.stderr, result.stderr
    stem = target.stem
    installed_package.run(f"""
from archive_line_index import build_line_index, open_content_stream, read_raw_index, read_sqlite_index
assert build_line_index({target.name!r}).tolist() == [3, 10, 11, 16]
assert read_sqlite_index({stem + ".sqlite3"!r}).tolist() == [3, 10, 11, 16]
assert read_raw_index({stem + ".u64"!r}).tolist() == [3, 10, 11, 16]
with open_content_stream({target.name!r}) as stream:
    assert stream.read() == b"\\xef\\xbb\\xbfalpha\\r\\n\\nomega"
""")
    bad = installed_package.workdir / ("corrupt-" + route + ".zip")
    with zipfile.ZipFile(bad, "w") as archive:
        archive.writestr("data", b"a\nb\n")
    raw = bytearray(bad.read_bytes())
    raw[34] ^= 1
    bad.write_bytes(raw)
    failure = _invoke(installed_package, route, [bad.name])
    assert failure.returncode == 1 and not failure.stdout and failure.stderr
    assert not bad.with_suffix(".sqlite3").exists()
    assert not bad.with_suffix(".u64").exists()


@pytest.mark.parametrize("route", ["console", "module", "imported"])
@pytest.mark.parametrize(
    "suffix,mode",
    [
        (".tar", "w"),
        (".tar.gz", "w:gz"),
        (".tgz", "w:gz"),
        (".tar.bz2", "w:bz2"),
        (".tbz", "w:bz2"),
        (".tbz2", "w:bz2"),
        (".tar.xz", "w:xz"),
        (".txz", "w:xz"),
    ],
)
def test_installed_tar_variants_and_pairs(
    installed_package: InstalledPackage, route: str, suffix: str, mode: str
) -> None:
    import tarfile

    from tests.helpers.archives import make_tar

    target = make_tar(
        installed_package.workdir
        / ("tar-" + route + suffix.replace(".", "_") + suffix),
        [("nested/data", b"\xef\xbb\xbfalpha\r\n\nomega", tarfile.REGTYPE)],
        mode=mode,
    )
    result = _invoke(installed_package, route, [target.name])
    assert result.returncode == 0 and not result.stderr, result.stderr
    stem = str(target.with_suffix(""))
    installed_package.run(f"""
from archive_line_index import build_line_index, read_raw_index, read_sqlite_index
assert build_line_index({target.name!r}, buffer_size=1).tolist() == [3, 10, 11, 16]
assert read_sqlite_index({stem + ".sqlite3"!r}).tolist() == [3, 10, 11, 16]
assert read_raw_index({stem + ".u64"!r}).tolist() == [3, 10, 11, 16]
""")


@pytest.mark.parametrize("mode", ["w", "w:gz", "w:bz2", "w:xz"])
def test_installed_empty_and_late_invalid_tar(
    installed_package: InstalledPackage, mode: str
) -> None:
    import tarfile

    from tests.helpers.archives import make_tar

    key = mode.replace(":", "-")
    empty = make_tar(
        installed_package.workdir / ("empty-" + key + ".tar"),
        [("data", b"", tarfile.REGTYPE)],
        mode=mode,
    )
    assert _invoke(installed_package, "console", [empty.name]).returncode == 0
    installed_package.run(f"""
from archive_line_index import read_raw_index, read_sqlite_index
assert read_raw_index({str(empty.with_suffix(".u64"))!r}).tolist() == [0]
assert read_sqlite_index({str(empty.with_suffix(".sqlite3"))!r}).tolist() == [0]
""")
    bad = make_tar(
        installed_package.workdir / ("late-" + key + ".tar"),
        [("data", b"a\nb", tarfile.REGTYPE), ("second", b"extra", tarfile.REGTYPE)],
        mode=mode,
    )
    result = _invoke(installed_package, "module", [bad.name])
    assert result.returncode == 1 and not result.stdout and result.stderr
    assert not bad.with_suffix(".sqlite3").exists()
    assert not bad.with_suffix(".u64").exists()
