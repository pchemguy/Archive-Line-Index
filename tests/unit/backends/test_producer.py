"""Bounded transport tests control producers and explicitly clean test threads."""

import threading

import pytest


def test_endpoint_subdivides_and_keeps_terminal_separate() -> None:
    from archive_stream.backends.producer import DataBlock, Finished, _Endpoint

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
    from archive_stream.backends.producer import _Cancelled, _Endpoint

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
    from archive_stream.backends.producer import DataBlock, Failed, _Endpoint

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
    from archive_stream.backends.producer import _Endpoint

    with pytest.raises(error):
        _Endpoint(queue_capacity=capacity, block_size=block)  # type: ignore[arg-type]


def test_empty_send_and_cancel_check_do_not_invent_data() -> None:
    from archive_stream.backends.producer import Finished, _Cancelled, _Endpoint

    endpoint = _Endpoint(queue_capacity=1, block_size=1)
    assert endpoint.send(b"") == 0
    endpoint.check_cancelled()
    endpoint.finish(None)
    assert isinstance(endpoint.receive(), Finished)
    endpoint.cancel()
    with pytest.raises(_Cancelled):
        endpoint.check_cancelled()


def test_worker_reader_fifo_failure_and_non_daemon_lifecycle() -> None:
    from archive_stream.backends.producer import start_queue_reader

    failure = ValueError("producer failed")
    workers: list[threading.Thread] = []

    def produce(endpoint: object) -> None:
        workers.append(threading.current_thread())
        endpoint.send(b"abcdef")  # type: ignore[attr-defined]
        raise failure

    reader = start_queue_reader(
        produce, declared_size=6, queue_capacity=1, block_size=2
    )
    try:
        assert reader.declared_size == 6
        assert b"".join(reader.read(1) for _ in range(6)) == b"abcdef"
        with pytest.raises(ValueError) as first:
            reader.read(99)
        assert first.value is failure and not reader.completed
        with pytest.raises(ValueError) as second:
            reader.read(1)
        assert second.value is failure
    finally:
        reader.close()
    assert len(workers) == 1 and not workers[0].daemon and not workers[0].is_alive()
    reader.close()
    with pytest.raises(ValueError):
        reader.read(1)


def test_full_queue_reader_close_joins_worker() -> None:
    from archive_stream.backends.producer import start_queue_reader

    def produce(endpoint: object) -> None:
        while True:
            endpoint.send(b"abcdefgh")  # type: ignore[attr-defined]

    reader = start_queue_reader(
        produce, declared_size=None, queue_capacity=1, block_size=2
    )
    try:
        assert reader.read(1) == b"a"
    finally:
        reader.close()
    assert not reader._thread.is_alive()
    assert not reader._endpoint.blocks and reader._current == b""


def test_empty_worker_success_and_invalid_sizes() -> None:
    from archive_stream.backends.producer import start_queue_reader

    reader = start_queue_reader(
        lambda endpoint: None, declared_size=0, queue_capacity=1, block_size=1
    )
    try:
        for value, error in [
            (0, ValueError),
            (-1, ValueError),
            (True, TypeError),
            (1.5, TypeError),
        ]:
            with pytest.raises(error):
                reader.read(value)  # type: ignore[arg-type]
        assert not reader.completed
        assert reader.read(1) == b"" and reader.completed
        assert reader.read(1) == b""
    finally:
        reader.close()


def test_start_failure_after_launch_cancels_and_joins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from archive_stream.backends.producer import start_queue_reader

    original = threading.Thread.start
    launched: list[threading.Thread] = []

    def start_then_fail(thread: threading.Thread) -> None:
        launched.append(thread)
        original(thread)
        raise RuntimeError("startup bookkeeping")

    def produce(endpoint: object) -> None:
        while True:
            endpoint.send(b"data")  # type: ignore[attr-defined]

    monkeypatch.setattr(threading.Thread, "start", start_then_fail)
    with pytest.raises(RuntimeError, match="startup bookkeeping"):
        start_queue_reader(produce, declared_size=None, queue_capacity=1, block_size=1)
    assert len(launched) == 1 and not launched[0].is_alive()


def test_join_failure_does_not_claim_closed_and_can_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from archive_stream.backends.producer import start_queue_reader

    reader = start_queue_reader(
        lambda endpoint: endpoint.send(b"x"),
        declared_size=1,
        queue_capacity=1,
        block_size=1,
    )
    with monkeypatch.context() as patcher:
        patcher.setattr(
            reader._thread, "join", lambda: (_ for _ in ()).throw(RuntimeError("join"))
        )
        with pytest.raises(RuntimeError, match="join"):
            reader.close()
    assert not reader._closed
    reader.close()
    assert reader._closed and not reader._thread.is_alive()


def test_close_wakes_waiting_reader_and_joins_producer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from archive_stream.backends.producer import start_queue_reader

    def produce(endpoint: object) -> None:
        while True:
            endpoint.check_cancelled()  # type: ignore[attr-defined]
            threading.Event().wait(0.01)

    reader = start_queue_reader(
        produce, declared_size=None, queue_capacity=1, block_size=1
    )
    entered = threading.Event()
    original = reader._endpoint.condition.wait

    def observed_wait(timeout: float | None = None) -> bool:
        entered.set()
        return original(timeout)

    monkeypatch.setattr(reader._endpoint.condition, "wait", observed_wait)
    errors: list[BaseException] = []

    def consume() -> None:
        try:
            reader.read(1)
        except BaseException as error:
            errors.append(error)

    consumer = threading.Thread(target=consume)
    consumer.start()
    try:
        assert entered.wait(2)
        reader.close()
    finally:
        reader.close()
        consumer.join(2)
    assert not consumer.is_alive() and not reader._thread.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], ValueError)


@pytest.mark.parametrize(
    "declared,error", [(True, TypeError), (-1, ValueError), (1.5, TypeError)]
)
def test_invalid_declared_size_does_not_start_worker(
    declared: object, error: type[Exception], monkeypatch: pytest.MonkeyPatch
) -> None:
    from archive_stream.backends.producer import start_queue_reader

    def forbidden(thread: threading.Thread) -> None:
        raise AssertionError("started with invalid options")

    monkeypatch.setattr(threading.Thread, "start", forbidden)
    with pytest.raises(error):
        start_queue_reader(
            lambda endpoint: None,
            declared_size=declared,
            queue_capacity=1,
            block_size=1,
        )  # type: ignore[arg-type]
