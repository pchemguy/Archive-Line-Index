"""Bounded transport tests control producers and explicitly clean test threads."""

import threading

import pytest


def test_endpoint_subdivides_and_keeps_terminal_separate() -> None:
    from archive_line_index.backends.producer import DataBlock, Finished, _Endpoint

    endpoint = _Endpoint(queue_capacity=1, block_size=2)
    errors: list[BaseException] = []

    def produce() -> None:
        try:
            assert endpoint.send(b"abcdef") == 6
            endpoint.finish(None)
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=produce)
    worker.start()
    try:
        assert [endpoint.receive() for _ in range(3)] == [
            DataBlock(b"ab"),
            DataBlock(b"cd"),
            DataBlock(b"ef"),
        ]
        assert isinstance(endpoint.receive(), Finished)
    finally:
        endpoint.cancel()
        worker.join(2)
    assert not worker.is_alive() and not errors


def test_full_queue_cancellation_unblocks_sender() -> None:
    from archive_line_index.backends.producer import _Cancelled, _Endpoint

    endpoint = _Endpoint(queue_capacity=1, block_size=1)
    errors: list[BaseException] = []

    def produce() -> None:
        try:
            endpoint.send(b"abc")
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=produce)
    worker.start()
    try:
        with endpoint.condition:
            assert endpoint.condition.wait_for(
                lambda: len(endpoint.blocks) == 1, timeout=2
            )
            assert not errors
        endpoint.cancel()
    finally:
        endpoint.cancel()
        worker.join(2)
    assert not worker.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], _Cancelled)


def test_terminal_failure_and_immutable_payload_snapshot() -> None:
    from archive_line_index.backends.producer import DataBlock, Failed, _Endpoint

    endpoint = _Endpoint(queue_capacity=2, block_size=8)
    data = bytearray(b"abc")
    assert endpoint.send(memoryview(data)) == 3
    data[:] = b"xyz"
    failure = ValueError("producer")
    endpoint.finish(failure)
    assert endpoint.receive() == DataBlock(b"abc")
    outcome = endpoint.receive()
    assert isinstance(outcome, Failed) and outcome.error is failure


@pytest.mark.parametrize(
    "capacity,block,error",
    [
        (0, 1, ValueError),
        (1, 0, ValueError),
        (-1, 1, ValueError),
        (True, 1, TypeError),
        (1, False, TypeError),
        (1.5, 1, TypeError),
        (1, float("inf"), TypeError),
    ],
)
def test_transport_settings_are_positive_finite_integers(
    capacity: object, block: object, error: type[Exception]
) -> None:
    from archive_line_index.backends.producer import _Endpoint

    with pytest.raises(error):
        _Endpoint(queue_capacity=capacity, block_size=block)  # type: ignore[arg-type]


def test_empty_send_and_cancel_check_do_not_invent_data() -> None:
    from archive_line_index.backends.producer import Finished, _Cancelled, _Endpoint

    endpoint = _Endpoint(queue_capacity=1, block_size=1)
    assert endpoint.send(b"") == 0
    endpoint.check_cancelled()
    endpoint.finish(None)
    assert isinstance(endpoint.receive(), Finished)
    endpoint.cancel()
    with pytest.raises(_Cancelled):
        endpoint.check_cancelled()
