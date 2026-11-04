"""Validate private native source/wheel inputs and their SHA256SUMS inventory.

Run with --dist DIST --tag vVERSION and optional --write-checksums. This helper
performs no hosted operations. Use scripts.prepare_release for the complete
version-free hosted asset inventory. Validation precedes checksum generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import Any

_FORBIDDEN = {
    ".agents",
    ".git",
    "ai-logs",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "dist",
    "build",
    "htmlcov",
    ".env",
    ".netrc",
    ".pypirc",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
}


def _safe_name(name: str) -> None:
    parts = name.rstrip("/").split("/")
    if (
        not name
        or name.startswith("/")
        or "\\" in name
        or ":" in name
        or any(ord(c) < 32 for c in name)
        or any(p in {"", ".", ".."} for p in parts)
    ):
        raise ValueError(f"Unsafe archive path: {name!r}")
    for part in parts:
        lower = part.lower()
        if (
            lower in _FORBIDDEN
            or lower.startswith(".coverage")
            or lower.endswith((".tkn", ".pyc", ".pyo", ".pem", ".key"))
        ):
            raise ValueError(f"Excluded distribution entry: {name}")


def _read_wheel(path: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as archive:
        seen: set[str] = set()
        for member in archive.infolist():
            _safe_name(member.filename)
            if member.filename in seen:
                raise ValueError("Duplicate wheel entry")
            seen.add(member.filename)
            mode = stat.S_IFMT(member.external_attr >> 16)
            if mode not in (0, stat.S_IFREG, stat.S_IFDIR) or member.flag_bits & 1:
                raise ValueError("Wheel contains a special or encrypted entry")
            if not member.is_dir():
                entries[member.filename] = archive.read(member)
    return entries


def _read_source(path: Path, root: str) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    seen: set[str] = set()
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            _safe_name(member.name)
            if member.name in seen:
                raise ValueError("Duplicate source entry")
            seen.add(member.name)
            parts = PurePosixPath(member.name).parts
            if parts[0] != root:
                raise ValueError("Source archive root disagrees with native filename")
            if member.isdir():
                continue
            if not member.isfile() or len(parts) < 2:
                raise ValueError("Source contains a special entry")
            handle = archive.extractfile(member)
            assert handle is not None
            with handle:
                entries["/".join(parts[1:])] = handle.read()
    return entries


def _require(entries: dict[str, bytes], required: set[str]) -> None:
    missing = required - entries.keys()
    if missing:
        raise ValueError(f"Missing distribution entries: {sorted(missing)}")


def _metadata(data: bytes, name: str, version: str, python: str) -> None:
    metadata = BytesParser().parsebytes(data)
    for field, expected in (
        ("Name", name),
        ("Version", version),
        ("Requires-Python", python),
    ):
        if metadata.get_all(field) != [expected]:
            raise ValueError(f"Distribution metadata {field} mismatch")


def check_release_artifacts(
    dist: Path, project: Path, tag: str, *, write_checksums: bool = False
) -> dict[str, str]:
    """Validate candidates against static project metadata and a v-prefixed tag.

    Returns filename-to-SHA256 mappings. Existing checksums are verified unless
    explicit generation was requested. Raises ValueError for invalid inventory.
    Ordinary file/decoding/archive errors remain visible to callers.
    """
    config: dict[str, Any] = tomllib.loads(project.read_text(encoding="utf-8"))[
        "project"
    ]
    name, version, python = config["name"], config["version"], config["requires-python"]
    if (
        not isinstance(version, str)
        or not re.fullmatch(r"\d+\.\d+\.\d+", version)
        or tag != "v" + version
    ):
        raise ValueError("Tag must exactly match the static project version")
    normalized = re.sub(r"[-_.]+", "_", name)
    base = f"{normalized}-{version}"
    wheel_name, source_name = base + "-py3-none-any.whl", base + ".tar.gz"
    expected = {wheel_name, source_name}
    files = list(dist.iterdir())
    if any(p.is_symlink() or not p.is_file() for p in files):
        raise ValueError("Inventory must contain ordinary files only")
    if {p.name for p in files} - {"SHA256SUMS"} != expected:
        raise ValueError(
            "Inventory requires exactly the native wheel and source distribution"
        )
    wheel = _read_wheel(dist / wheel_name)
    source = _read_source(dist / source_name, base)
    info = base + ".dist-info/"
    package = normalized + "/"
    _require(
        wheel,
        {
            package + "__init__.py",
            package + "py.typed",
            info + "METADATA",
            info + "WHEEL",
            info + "RECORD",
        },
    )
    if any(not n.startswith((package, info)) for n in wheel):
        raise ValueError("Wheel contains files outside its package/metadata")
    _require(
        source,
        {
            "pyproject.toml",
            "PKG-INFO",
            "README.md",
            "LICENSE",
            "src/" + package + "__init__.py",
            "src/" + package + "py.typed",
        },
    )
    _metadata(wheel[info + "METADATA"], name, version, python)
    _metadata(source["PKG-INFO"], name, version, python)
    wheel_metadata = BytesParser().parsebytes(wheel[info + "WHEEL"])
    if (
        wheel_metadata.get_all("Tag") != ["py3-none-any"]
        or wheel_metadata["Root-Is-Purelib"] != "true"
    ):
        raise ValueError("Wheel tags disagree with its native filename")
    embedded = tomllib.loads(source["pyproject.toml"].decode("utf-8"))["project"]
    if any(
        embedded.get(key) != config[key]
        for key in ("name", "version", "requires-python")
    ):
        raise ValueError("Source build metadata mismatch")
    wheel_package = {n: data for n, data in wheel.items() if n.startswith(package)}
    source_package = {
        n[4:]: data for n, data in source.items() if n.startswith("src/" + package)
    }
    if wheel_package != source_package:
        raise ValueError("Source and wheel package inventories/bytes differ")
    hashes: dict[str, str] = {}
    for filename in sorted(expected):
        with (dist / filename).open("rb") as handle:
            hashes[filename] = hashlib.file_digest(handle, "sha256").hexdigest()
    content = "".join(f"{digest}  {filename}\n" for filename, digest in hashes.items())
    checksums = dist / "SHA256SUMS"
    if write_checksums:
        checksums.write_text(content, encoding="ascii")
    elif not checksums.is_file() or checksums.read_text(encoding="ascii") != content:
        raise ValueError("SHA256SUMS missing or checksum inventory mismatch")
    return hashes


def main() -> int:
    """Run deterministic local validation, returning a useful process status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--write-checksums", action="store_true")
    args = parser.parse_args()
    try:
        result = check_release_artifacts(
            args.dist, args.pyproject, args.tag, write_checksums=args.write_checksums
        )
    except (
        ValueError,
        KeyError,
        OSError,
        EOFError,
        tarfile.TarError,
        zipfile.BadZipFile,
    ) as error:
        parser.exit(1, f"Artifact validation failed: {error}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
