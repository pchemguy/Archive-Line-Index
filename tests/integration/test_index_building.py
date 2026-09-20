"""Integration tests for direct and composed plain-source indexing."""

from __future__ import annotations

import io

import pytest

from archive_line_index import (
    SizeLimitExceededError,
    build_line_index,
    scan_line_offsets,
)
from tests.helpers.binary_cases import BINARY_CASES, UTF8_BOM


@pytest.mark.parametrize("case", BINARY_CASES, ids=lambda case: case.name)
def test_path_build_matches_direct_stream_scan(tmp_path, case) -> None:
    path = tmp_path / f"{case.name}.jsonl"
    path.write_bytes(case.content)

    direct = scan_line_offsets(
        io.BytesIO(case.content),
        skip_utf8_bom=case.skip_bom,
        buffer_size=2,
    )
    composed = build_line_index(
        path,
        skip_utf8_bom=case.skip_bom,
        buffer_size=2,
    )

    assert tuple(direct) == case.offsets
    assert composed == direct


def test_caller_stream_build_uses_current_position_and_preserves_ownership() -> None:
    source = io.BytesIO(b"ignored" + UTF8_BOM + b"a\n\nb")
    source.seek(len(b"ignored"))

    offsets = build_line_index(source, buffer_size=1)

    assert tuple(offsets) == (3, 5, 6, 7)
    assert not source.closed


def test_bom_policy_changes_only_the_first_line_start() -> None:
    content = UTF8_BOM + b"a\nb"

    skipped = build_line_index(io.BytesIO(content), skip_utf8_bom=True)
    retained = build_line_index(io.BytesIO(content), skip_utf8_bom=False)

    assert tuple(skipped) == (3, 5, 6)
    assert tuple(retained) == (0, 5, 6)


def test_maximum_size_is_applied_to_composed_build() -> None:
    source = io.BytesIO(b"a\nb")

    with pytest.raises(SizeLimitExceededError):
        build_line_index(source, max_uncompressed_size=2)

    assert not source.closed


@pytest.mark.parametrize(
    ("keyword", "value", "error"),
    [
        ("skip_utf8_bom", 1, TypeError),
        ("buffer_size", True, TypeError),
        ("buffer_size", 0, ValueError),
        ("max_uncompressed_size", True, TypeError),
        ("max_uncompressed_size", -1, ValueError),
    ],
)
def test_invalid_options_fail_before_path_open(tmp_path, keyword, value, error) -> None:
    options = {keyword: value}
    with pytest.raises(error):
        build_line_index(tmp_path / "missing.jsonl", **options)
