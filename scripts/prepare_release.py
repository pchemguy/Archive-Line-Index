"""Build/check stable release bundles containing ecosystem-valid native packages.

Invoke from the project root with python -m scripts.prepare_release. The native
build directory is private build input; the output is the complete flat hosted
asset inventory. This command never tags, uploads or publishes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path

from scripts.check_release_artifacts import check_release_artifacts
from scripts.release_names import check_names

ASSET_NAMES = [
    "archive-stream-wheel.zip",
    "archive-stream-source.zip",
    "SHA256SUMS",
]


def _version(project: Path, tag: str) -> str:
    version = str(
        tomllib.loads(project.read_text(encoding="utf-8"))["project"]["version"]
    )
    if tag != "v" + version:
        raise ValueError("Release tag disagrees with package metadata")
    return version


def check_bundles(
    directory: Path, project: Path, tag: str, *, write_checksums: bool = False
) -> dict[str, str]:
    """Validate complete outer names, safe contents, native metadata and hashes."""
    version = _version(project, tag)
    files = list(directory.iterdir())
    if directory.is_symlink() or any(p.is_symlink() or not p.is_file() for p in files):
        raise ValueError("Release staging requires ordinary files only")
    check_names(
        ASSET_NAMES, [p.name for p in files], version, complete=not write_checksums
    )
    native_names = [
        f"archive_stream-{version}-py3-none-any.whl",
        f"archive_stream-{version}.tar.gz",
    ]
    with tempfile.TemporaryDirectory() as temporary:
        native = Path(temporary)
        for asset, name in zip(ASSET_NAMES[:2], native_names, strict=True):
            with zipfile.ZipFile(directory / asset) as archive:
                entries = archive.infolist()
                if (
                    len(entries) != 1
                    or entries[0].filename != name
                    or entries[0].is_dir()
                    or entries[0].flag_bits & 1
                ):
                    raise ValueError(
                        "Release bundle must contain exactly its native package"
                    )
                mode = entries[0].external_attr >> 16
                if mode & 0o170000 not in (0, 0o100000):
                    raise ValueError("Release bundle contains a special entry")
                (native / name).write_bytes(archive.read(entries[0]))
        check_release_artifacts(native, project, tag, write_checksums=True)
    hashes = {
        name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
        for name in ASSET_NAMES[:2]
    }
    manifest = "".join(f"{digest}  {name}\n" for name, digest in sorted(hashes.items()))
    checksum = directory / "SHA256SUMS"
    if write_checksums:
        checksum.write_text(manifest, encoding="ascii")
    elif not checksum.is_file() or checksum.read_text(encoding="ascii") != manifest:
        raise ValueError("Release bundle checksum mismatch")
    check_names(ASSET_NAMES, [p.name for p in directory.iterdir()], version)
    return hashes


def prepare_bundles(
    native: Path, directory: Path, project: Path, tag: str
) -> dict[str, str]:
    """Validate native inputs and create a new complete stable asset set."""
    if directory.is_symlink():
        raise ValueError("Release staging requires an ordinary directory")
    version = _version(project, tag)
    check_names(ASSET_NAMES, ASSET_NAMES, version)
    check_release_artifacts(native, project, tag, write_checksums=True)
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("Use an empty release staging directory")
    names = [
        f"archive_stream-{version}-py3-none-any.whl",
        f"archive_stream-{version}.tar.gz",
    ]
    for asset, name in zip(ASSET_NAMES[:2], names, strict=True):
        info = zipfile.ZipInfo(name)
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        with zipfile.ZipFile(directory / asset, "x") as archive:
            archive.writestr(info, (native / name).read_bytes())
    return check_bundles(directory, project, tag, write_checksums=True)


def main() -> int:
    """Build or independently check the exact staged release inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-dist", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            result = check_bundles(args.output, args.pyproject, args.tag)
        else:
            if args.native_dist is None:
                raise ValueError("--native-dist is required when building bundles")
            result = prepare_bundles(
                args.native_dist, args.output, args.pyproject, args.tag
            )
    except (
        ValueError,
        OSError,
        EOFError,
        tarfile.TarError,
        zipfile.BadZipFile,
    ) as error:
        parser.exit(1, f"Release artifact validation failed: {error}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
