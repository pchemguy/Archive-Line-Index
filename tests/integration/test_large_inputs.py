"""Slow generated-scale verification for bounded streaming and indexing.

RSS checks sample this test process immediately before and during a bounded
read loop. Their limits apply to the observed incremental resident set, not to
absolute interpreter memory or a portable peak-watermark guarantee. Running
the slow suite separately reduces allocator reuse that could conceal growth;
the 7z allowance also includes memory retained by dependency callbacks. On
Linux, ``/proc/self`` resolves the actual process even when container and proc
PID namespaces differ; other platforms use psutil's current process lookup.
"""

from __future__ import annotations

import gc
import mmap
import os
from pathlib import Path
import sys
import tracemalloc

import psutil
import py7zr
import pytest

from archive_line_index import (
    SizeLimitExceededError,
    build_line_index,
    open_content_stream,
)


pytestmark = pytest.mark.slow

MEBIBYTE = 1024 * 1024
READ_SIZE = 64 * 1024


def _write_repeated(path: Path, block: bytes, total_size: int) -> None:
    """Write exactly ``total_size`` bytes without constructing them at once."""

    assert total_size % len(block) == 0
    with path.open("wb") as stream:
        for _ in range(total_size // len(block)):
            stream.write(block)


def _rss() -> int:
    """Sample current-process RSS; this is not a historical peak reading."""

    if sys.platform == "linux":
        resident_pages = int(Path("/proc/self/statm").read_text().split()[1])
        return resident_pages * os.sysconf("SC_PAGE_SIZE")
    return psutil.Process().memory_info().rss


def test_rss_sampler_tracks_this_process() -> None:
    gc.collect()
    baseline = _rss()
    with mmap.mmap(-1, 32 * MEBIBYTE) as allocation:
        for offset in range(0, len(allocation), mmap.PAGESIZE):
            allocation[offset] = 1
        assert _rss() - baseline > 16 * MEBIBYTE


def test_large_plain_payload_streams_with_bounded_process_memory(tmp_path) -> None:
    payload_size = 64 * MEBIBYTE
    source = tmp_path / "large.bin"
    _write_repeated(source, b"0123456789abcdef" * 4096, payload_size)
    gc.collect()
    baseline = peak = _rss()
    consumed = 0

    with open_content_stream(source) as stream:
        while chunk := stream.read(READ_SIZE):
            consumed += len(chunk)
            peak = max(peak, _rss())
            assert len(chunk) <= READ_SIZE

    assert consumed == payload_size
    assert peak - baseline < 16 * MEBIBYTE


def test_line_far_larger_than_scan_buffer_is_not_retained(tmp_path) -> None:
    line_size = 16 * MEBIBYTE
    source = tmp_path / "long-line.txt"
    _write_repeated(source, b"x" * READ_SIZE, line_size)
    with source.open("ab") as stream:
        stream.write(b"\nend")

    tracemalloc.start()
    try:
        offsets = build_line_index(source, buffer_size=READ_SIZE)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert tuple(offsets) == (0, line_size + 1, line_size + 4)
    assert peak < 4 * MEBIBYTE


def test_millions_of_short_lines_use_about_eight_bytes_each(tmp_path) -> None:
    line_count = 2_000_000
    source = tmp_path / "many-lines.txt"
    _write_repeated(source, b"x\n" * 10_000, line_count * 2)

    offsets = build_line_index(source)

    assert len(offsets) == line_count + 1
    assert offsets.itemsize == 8
    assert offsets[0] == 0
    assert offsets[-1] == line_count * 2
    assert sys.getsizeof(offsets) <= len(offsets) * 9 + 1024


def test_highly_compressible_7z_expands_through_bounded_reads(tmp_path) -> None:
    payload_size = 256 * MEBIBYTE
    source = tmp_path / "compressible.bin"
    archive_path = tmp_path / "compressible.7z"
    _write_repeated(source, b"z" * READ_SIZE, payload_size)
    with py7zr.SevenZipFile(archive_path, "w") as archive:
        archive.write(source, arcname="payload.bin")
    source.unlink()

    assert archive_path.stat().st_size < payload_size // 100
    with pytest.raises(SizeLimitExceededError):
        open_content_stream(
            archive_path,
            max_uncompressed_size=payload_size - 1,
        )

    gc.collect()
    baseline = peak = _rss()
    consumed = 0
    with open_content_stream(archive_path) as stream:
        while chunk := stream.read(READ_SIZE):
            consumed += len(chunk)
            peak = max(peak, _rss())
            assert len(chunk) <= READ_SIZE

    assert consumed == payload_size
    assert peak - baseline < 224 * MEBIBYTE
