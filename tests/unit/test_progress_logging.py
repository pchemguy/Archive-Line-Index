"""Byte progress is chunk-bounded, correctly timed and application-configured."""

import io
import logging
from unittest.mock import Mock

import pytest
from tests.helpers.readers import Reader

from archive_stream import InvalidIndexError, scan_line_offsets, scanner

LOGGER = "archive_stream.scanner"


def messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.name == LOGGER]


@pytest.mark.parametrize(
    "payload,expected",
    [
        (b"", [0]),
        (b"\xef\xbb\xbf", [3]),
        (b"a\nb", [0, 2, 3]),
        (b"\xef\xbb\xbfa\r\n\nz", [3, 6, 7, 8]),
    ],
)
def test_scan_completion_uses_original_uncompressed_bytes(
    caplog: pytest.LogCaptureFixture, payload: bytes, expected: list[int]
) -> None:
    source = io.BytesIO(payload)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert scan_line_offsets(source, buffer_size=1).tolist() == expected
    assert messages(caplog)[-1] == f"Scan complete: {len(payload)} uncompressed bytes"
    assert not source.closed


def test_one_second_boundary_no_catchup_and_exact_final(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Mock(side_effect=[0.0, 0.999, 1.0, 99.0])
    monkeypatch.setattr(scanner, "monotonic", clock, raising=False)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert scan_line_offsets(io.BytesIO(b"abc\nd\nz"), buffer_size=3).tolist() == [
            0,
            4,
            6,
            7,
        ]
    assert messages(caplog) == [
        "Scanned 6 B of uncompressed data",
        "Scanned 6 B of uncompressed data",
        "Scan complete: 7 uncompressed bytes",
    ]
    assert clock.call_count == 4


def test_completed_buffer_capacity_across_bom_and_short_reads(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = Reader(b"\xef", b"\xbb\xbf", b"a", b"b\nc", b"de")
    monkeypatch.setattr(scanner, "monotonic", Mock(side_effect=[0, 1, 2, 3, 4]))
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert scan_line_offsets(source, buffer_size=4).tolist() == [3, 6, 9]
    assert messages(caplog) == [
        "Scanned 0 B of uncompressed data",
        "Scanned 4 B of uncompressed data",
        "Scanned 4 B of uncompressed data",
        "Scanned 8 B of uncompressed data",
        "Scan complete: 9 uncompressed bytes",
    ]


@pytest.mark.parametrize(
    ("buffer_size", "position", "expected"),
    [
        (1, 1023, "1023 B"),
        (1, 1024, "1.00 KiB"),
        (1, 1152, "1.13 KiB"),
        (10, 1530, "1.5 KiB"),
        (11, 1540, "2 KiB"),
        (1, 1023 * 1024 + 512, "1023.50 KiB"),
        (1024**2, 1023 * 1024**2, "1023 MiB"),
        (512 * 1024, 1024**3 - 512 * 1024, "1.00 GiB"),
        (1024**2, 3 * 1024**3 // 2, "1.50 GiB"),
        (1024**2, 1024**4, "1.00000 TiB"),
        (1024**2, 2**63 - 1, "8.00000000000 EiB"),
    ],
)
def test_periodic_report_precision_and_binary_unit_promotion(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    buffer_size: int,
    position: int,
    expected: str,
) -> None:
    monkeypatch.setattr(scanner, "monotonic", Mock(side_effect=[0, 1]))
    with caplog.at_level(logging.INFO, logger=LOGGER):
        progress = scanner._ScanProgress(buffer_size=buffer_size)
        progress.update(position)
    assert messages(caplog) == [f"Scanned {expected} of uncompressed data"]


def test_disabled_progress_has_no_clock_or_info_calls(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    forbidden = Mock(side_effect=AssertionError("disabled progress did work"))
    monkeypatch.setattr(scanner, "monotonic", forbidden, raising=False)
    monkeypatch.setattr(logging.getLogger(LOGGER), "info", forbidden)
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        assert scan_line_offsets(io.BytesIO(b"a\n" * 200), buffer_size=4)[-1] == 400
    assert forbidden.call_count == 0 and not messages(caplog)


def test_enabled_observation_cost_depends_on_chunks_not_lines(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Mock(return_value=0.0)
    monkeypatch.setattr(scanner, "monotonic", clock, raising=False)
    counts = []
    with caplog.at_level(logging.INFO, logger=LOGGER):
        for payload in [b"x" * 64, b"\n" * 64]:
            clock.reset_mock()
            scan_line_offsets(io.BytesIO(payload), buffer_size=8)
            counts.append(clock.call_count)
    assert counts[0] == counts[1] and 1 < counts[0] <= 11
    assert len(messages(caplog)) == 2


@pytest.mark.parametrize(
    "error",
    [OSError("read"), KeyboardInterrupt(), MemoryError()],
    ids=["source", "interrupt", "memory"],
)
def test_failed_scan_never_claims_completion(
    caplog: pytest.LogCaptureFixture, error: BaseException
) -> None:
    source = Reader(b"abc", error)
    with caplog.at_level(logging.INFO, logger=LOGGER), pytest.raises(type(error)):
        scan_line_offsets(source)
    assert not any(m.startswith("Scan complete:") for m in messages(caplog))
    assert source.closes == 0


def test_index_validation_failure_never_claims_completion(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        scanner, "validate_offsets", Mock(side_effect=InvalidIndexError("invalid"))
    )
    with caplog.at_level(logging.INFO, logger=LOGGER), pytest.raises(InvalidIndexError):
        scan_line_offsets(io.BytesIO(b"a\nb"))
    assert not any(m.startswith("Scan complete:") for m in messages(caplog))


def test_scans_have_independent_timer_state(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        scanner, "monotonic", Mock(side_effect=[0.0, 1.0, 100.0, 100.1]), raising=False
    )
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scan_line_offsets(io.BytesIO(b"abc"), buffer_size=3)
        scan_line_offsets(io.BytesIO(b"x"))
    assert messages(caplog) == [
        "Scanned 3 B of uncompressed data",
        "Scan complete: 3 uncompressed bytes",
        "Scan complete: 1 uncompressed bytes",
    ]
