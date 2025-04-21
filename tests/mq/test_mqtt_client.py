import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from caqes_core.mq.mqtt.mqtt_client import MqttClient
from settings.worker_settings import WorkerSettings


@pytest_asyncio.fixture
async def mqtt_client():
    """
    Fixture that creates a mock MQTT client instance
    """
    client = MqttClient()
    client.client = Mock()
    return client


@pytest.mark.asyncio
async def test_connect_success(mqtt_client: MqttClient):
    """
    Test successful connection to MQTT broker
    """
    # Mock configuration
    mqtt_settings = {
        "username": "test_user",
        "password": "test_pass",
        "host": "test_host",
        "port": 1883,
        "max_retries": 3,
        "retry_delay": 0.1,
    }
    mqtt_client.settings = MQSettings(**mqtt_settings)
    mqtt_client.loop = asyncio.get_event_loop()

    # Set up the mock to trigger on_connect callback
    def mock_connect(*args, **kwargs):
        # Simulate successful connection by calling _on_connect with rc=0
        mqtt_client._on_connect(None, None, None, 0)
        return None

    mqtt_client.client.connect.side_effect = mock_connect

    # Call connect method
    await mqtt_client.connect()

    # Verify connection setup
    mqtt_client.client.username_pw_set.assert_called_once_with(
        "test_user", "test_pass")
    mqtt_client.client.connect.assert_called_once_with("test_host", 1883)
    mqtt_client.client.loop_start.assert_called_once()


@pytest.mark.asyncio
async def test_connect_failure(mqtt_client: MqttClient):
    """
    Test connection failure to MQTT broker
    """
    mqtt_settings = {
        "username": "test_user",
        "password": "test_pass",
        "host": "test_host",
        "port": 1883,
        "max_retries": 3,
        "retry_delay": 0.1,
    }
    mqtt_client.settings = MQSettings(**mqtt_settings)
    mqtt_client.loop = asyncio.get_event_loop()

    def mock_connect(*args, **kwargs):
        mqtt_client._on_connect(None, None, None, 1)
        return None

    mqtt_client.client.connect.side_effect = mock_connect

    with pytest.raises(ConnectionError) as e:
        await mqtt_client.connect()

    # Verify connection setup
    assert str(e.value).__contains__("Failed to connect after")


@pytest.mark.asyncio
async def test_connect_retry_success_last(mqtt_client):
    """
    Test connection retry mechanism with success on the last retry
    """
    # Mock configuration
    mqtt_settings = {
        "username": "test_user",
        "password": "test_pass",
        "host": "test_host",
        "port": 1883,
        "max_retries": 3,
        "retry_delay": 0.1,
    }
    mqtt_client.settings = MQSettings(**mqtt_settings)
    mqtt_client.loop = asyncio.get_event_loop()

    retry_count = 0  # Initialize retry count

    def mock_connect(*args, **kwargs):
        nonlocal retry_count
        retry_count += 1
        if retry_count < mqtt_settings["max_retries"]:
            mqtt_client._on_connect(None, None, None, 1)  # Simulate failure
        else:
            mqtt_client._on_connect(None, None, None, 0)  # Simulate success

    mqtt_client.client.connect.side_effect = mock_connect

    await mqtt_client.connect()  # No exception should be raised.

    assert mqtt_client.client.username_pw_set.call_count == mqtt_settings["max_retries"]
    assert mqtt_client.client.connect.call_count == mqtt_settings["max_retries"]
    assert mqtt_client.client.loop_start.call_count == mqtt_settings["max_retries"]


@pytest.mark.asyncio
async def test_close(mqtt_client):
    """
    Test the close method
    """
    # Mock the client methods
    mqtt_client.client.loop_stop = AsyncMock()
    mqtt_client.client.disconnect = AsyncMock()

    await mqtt_client.close()

    mqtt_client.client.loop_stop.assert_called_once()
    mqtt_client.client.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_subscribe_success(mqtt_client):
    # Set up connected state
    mqtt_client.connected = True
    mqtt_client.client.subscribe = AsyncMock()
    callback = AsyncMock()

    await mqtt_client.subscribe("test/topic", callback)

    mqtt_client.client.subscribe.assert_called_once_with("test/topic")
    assert mqtt_client.callback == callback


@pytest.mark.asyncio
async def test_subscribe_not_connected(mqtt_client: MqttClient):
    """
    Test subscription when client it not connected
    """
    # Set up disconnected state
    mqtt_client.client.subscribe = AsyncMock()
    mqtt_client.is_connected = AsyncMock()
    mqtt_client.is_connected.return_value = False
    callback = AsyncMock()

    with pytest.raises(RuntimeError) as excinfo:
        await mqtt_client.subscribe("test/topic", callback)

    assert str(excinfo.value) == "Not connected to MQTT broker"
    mqtt_client.client.subscribe.assert_not_called()
    assert mqtt_client.callback is None  # or whatever default value.


@pytest.mark.asyncio
async def test_subscribe_empty_topic(mqtt_client):
    """
    Test subscription with an empty topic string.
    """
    # Arrange
    mqtt_client.connected = True
    mqtt_client.client.subscribe = MagicMock()
    mqtt_client.client.subscribe.side_effect = ValueError(
        "invalid topic value")
    callback = AsyncMock()
    topic = None

    # Act
    with pytest.raises(ValueError) as exc_info:
        await mqtt_client.subscribe(topic, callback)

    # Assert
    assert str(exc_info.value) == "invalid topic value"
    mqtt_client.client.subscribe.assert_called_once()
