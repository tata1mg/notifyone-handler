"""
Unit tests for handler KafkaWrapper.
Stubs out commonutils/torpedo so this runs without the full pipenv install.
"""
import asyncio
import functools
import importlib.util
import os
import json
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def run_async(coro_func):
    """Run an async test on a private event loop, leaving the ambient loop untouched.

    Keeps these tests independent of pytest-sanic / pytest-asyncio loop management
    so they cannot interfere with the session-scoped fixtures of other tests.
    """
    @functools.wraps(coro_func)
    def wrapper(*args, **kwargs):
        try:
            prev_loop = asyncio.get_event_loop()
        except RuntimeError:
            prev_loop = None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro_func(*args, **kwargs))
        finally:
            loop.close()
            asyncio.set_event_loop(prev_loop)
    return wrapper



# ---------------------------------------------------------------------------
# Bootstrap stubs
# ---------------------------------------------------------------------------

def _ensure_stub(name, **attrs):
    if name not in sys.modules:
        mod = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(mod, k, v)
        sys.modules[name] = mod
    return sys.modules[name]


_ensure_stub("commonutils", BaseSQSWrapper=object)
_ensure_stub("commonutils.utils", CustomEnum=str)
_ensure_stub("commonutils.handlers")
_ensure_stub("commonutils.handlers.sqs", SQSHandler=object)
_ensure_stub("torpedo")
_ensure_stub("torpedo.exceptions")

_HANDLER_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _HANDLER_ROOT not in sys.path:
    sys.path.insert(0, _HANDLER_ROOT)

_spec = importlib.util.spec_from_file_location(
    "handler_kafka_wrapper",
    f"{_HANDLER_ROOT}/app/pubsub/kafka/kafka_wrapper.py",
)
_kafka_wrapper_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kafka_wrapper_mod)

KafkaWrapper = _kafka_wrapper_mod.KafkaWrapper


# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def kafka_config():
    return {
        "KAFKA": {
            "BOOTSTRAP_SERVERS": "localhost:9092",
            "MAX_RETRY_ATTEMPTS": 3,
        }
    }


def _make_mock_msg(body_bytes, partition=0, offset=0, topic="test-topic"):
    msg = MagicMock()
    msg.value = body_bytes
    msg.headers = []
    msg.partition = partition
    msg.offset = offset
    msg.topic = topic
    return msg


class _AsyncIter:
    def __init__(self, items):
        self._it = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration


def _make_mock_consumer(msgs):
    mock_consumer = MagicMock()
    mock_consumer.start = AsyncMock()
    mock_consumer.stop = AsyncMock()
    mock_consumer.commit = AsyncMock()
    mock_consumer.seek = MagicMock()  # synchronous per aiokafka==0.10.0 API
    mock_consumer.__aiter__ = lambda self: _AsyncIter(msgs)
    return mock_consumer


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@run_async
async def test_publish_to_kafka_sends_utf8_bytes_to_correct_topic(kafka_config):
    """publish_to_kafka sends UTF-8 bytes to correct topic."""
    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer") as MockProducer:
        mock_producer = AsyncMock()
        MockProducer.return_value = mock_producer
        mock_producer.send_and_wait = AsyncMock(return_value=None)

        wrapper = KafkaWrapper(config=kafka_config)
        await wrapper.get_kafka_client("test-topic")
        await wrapper.publish_to_kafka(payload='{"hello": "world"}')

    call_args = mock_producer.send_and_wait.call_args
    topic_arg = call_args.args[0] if call_args.args else call_args[0][0]
    value_arg = call_args.kwargs.get("value") or call_args[1].get("value")
    assert topic_arg == "test-topic"
    assert value_arg == b'{"hello": "world"}'


@run_async
async def test_subscribe_all_calls_handler_with_decoded_data(kafka_config):
    """subscribe_all calls handler.handle_event with decoded data."""
    body = json.dumps({"msg": "hello"})
    msg = _make_mock_msg(body.encode("utf-8"))
    mock_consumer = _make_mock_consumer([msg])

    handler = MagicMock()
    handler.handle_event = AsyncMock(return_value=True)

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(config=kafka_config)
        await wrapper.subscribe_all(
            handler,
            topic_name="test-topic",
            group_id="ns-handler-sms",
            max_no_of_messages=5,
        )

    handler.handle_event.assert_called_once_with(body)


@run_async
async def test_subscribe_all_retry_then_skip_after_max_attempts(kafka_config):
    """After MAX_RETRY_ATTEMPTS failures the message is committed (skipped).
    handler.handle_event must be called exactly MAX_RETRY_ATTEMPTS (3) times."""
    cfg = {"KAFKA": {"BOOTSTRAP_SERVERS": "localhost:9092", "MAX_RETRY_ATTEMPTS": 3}}
    body = json.dumps({"x": 1})
    # Same offset = same logical message; inject 3 copies to simulate the seek()
    # re-delivery that occurs after each failure below the threshold.
    msgs = [
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=1),
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=1),
        _make_mock_msg(body.encode("utf-8"), partition=0, offset=1),
    ]
    mock_consumer = _make_mock_consumer(msgs)

    handler = MagicMock()
    handler.handle_event = AsyncMock(side_effect=Exception("handler failed"))

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(config=cfg)
        await wrapper.subscribe_all(
            handler,
            topic_name="test-topic",
            group_id="ns-handler-sms",
            max_no_of_messages=5,
        )

    # handler must be called exactly MAX_RETRY_ATTEMPTS times
    assert handler.handle_event.call_count == 3
    # After 3 failures, must commit exactly once to skip poison-pill
    mock_consumer.commit.assert_called_once()


@run_async
async def test_subscribe_all_seek_called_on_failure_below_threshold(kafka_config):
    """consumer.seek() is called with the correct TopicPartition and offset when
    handle_event raises and retry_count is below MAX_RETRY_ATTEMPTS."""
    cfg = {"KAFKA": {"BOOTSTRAP_SERVERS": "localhost:9092", "MAX_RETRY_ATTEMPTS": 3}}
    body = json.dumps({"x": 1})
    # Only one delivery — count 1 < threshold 3
    msg = _make_mock_msg(body.encode("utf-8"), partition=2, offset=99, topic="test-topic")
    mock_consumer = _make_mock_consumer([msg])

    handler = MagicMock()
    handler.handle_event = AsyncMock(side_effect=Exception("transient error"))

    with patch.object(_kafka_wrapper_mod, "AIOKafkaProducer"), \
         patch.object(_kafka_wrapper_mod, "AIOKafkaConsumer") as MockConsumer, \
         patch.object(_kafka_wrapper_mod, "TopicPartition") as MockTP:
        MockConsumer.return_value = mock_consumer

        wrapper = KafkaWrapper(config=cfg)
        await wrapper.subscribe_all(
            handler,
            topic_name="test-topic",
            group_id="ns-handler-sms",
            max_no_of_messages=5,
        )

    # No commit — message is below threshold
    mock_consumer.commit.assert_not_called()
    # seek() must be called to reschedule re-delivery within the same session
    mock_consumer.seek.assert_called_once()
    MockTP.assert_called_once_with("test-topic", 2)  # topic_name, partition
