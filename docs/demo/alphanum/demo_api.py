"""Build both line-index formats for each Alphanum fixture from the checkout."""

import sys
from pathlib import Path


def main() -> None:
    """Index all six inputs through the public Python API."""
    demo_dir = Path(__file__).resolve().parent
    # Use checkout sources as if the repository's src directory were on PYTHONPATH.
    sys.path.insert(0, str(demo_dir.parents[2] / "src"))

    from archive_stream import build_line_index, write_raw_index, write_sqlite_index

    for extension in ("txt", "7z", "zip", "tar", "tbz", "tgz"):
        target = demo_dir / extension / f"demo.{extension}"
        sqlite = target.with_suffix(".sqlite3")
        raw = target.with_suffix(".u64")
        offsets = build_line_index(target)
        write_sqlite_index(offsets, sqlite)
        write_raw_index(offsets, raw)
        print(f"Indexed {len(offsets) - 1} lines: {sqlite}; {raw}")


if __name__ == "__main__":
    main()
