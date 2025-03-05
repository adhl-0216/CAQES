import json
from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest_asyncio
from config.settings import NatsSettings

from alerts.alert_listener import AlertListener

pytest_plugins = ['pytest_asyncio']


@pytest_asyncio.fixture
async def listener() -> AlertListener:
    """
    Fixture that creates a mock AlertListener instance with mocked NATS connection.
    """
    listener = AlertListener()
    listener.nc = AsyncMock()
    listener.js = AsyncMock()
    return listener


@pytest.mark.asyncio
@patch('nats.connect')
async def test_connect(mock_connect):
    """
    Verifies that the NATS connection is established with correct URL
    """
    mock_js = AsyncMock()
    mock_nc = AsyncMock()
    mock_nc.jetstream = AsyncMock(return_value=mock_js)
    mock_connect.return_value = mock_nc

    listener = AlertListener()
    await listener.connect()

    mock_connect.assert_called_once_with("nats://nats:4222")
    mock_nc.jetstream.assert_called_once()


@pytest.mark.asyncio
@patch('nats.connect')
async def test_connect_error(mock_connect):
    """
    Verifies error handling when connection fails
    """
    error = Exception("Connection failed")
    mock_connect.side_effect = error

    listener = AlertListener()
    with pytest.raises(Exception) as exc_info:
        await listener.connect()

    assert str(exc_info.value) == "Connection failed"


@pytest.mark.asyncio
@patch('nats.connect')
async def test_connect_with_retry(mock_connect):
    """
    Verifies that connection retries work as expected
    """
    mock_js = AsyncMock()
    mock_nc = AsyncMock()
    mock_nc.jetstream = AsyncMock(return_value=mock_js)

    mock_connect.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        mock_nc
    ]

    listener = AlertListener()
    await listener.connect()

    assert mock_connect.call_count == 3
    assert listener.nc == mock_nc
    assert listener.js == mock_js


@pytest.mark.asyncio
@patch('nats.connect')
async def test_connect_retry_exhausted(mock_connect):
    """
    Verifies that connection fails after all retries are exhausted
    """
    mock_connect.side_effect = Exception("Connection failed")
    listener = AlertListener()
    with pytest.raises(ConnectionError) as exc_info:
        await listener.connect()

    assert mock_connect.call_count == 3
    assert str(
        exc_info.value) == f"Failed to connect after 3 attempts. Last error: Connection failed"


async def test_close(listener: AlertListener):
    """
    Verifies that the NATS connection is closed when the listener is terminated.
    """
    await listener.close()

    listener.nc.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_error(listener: AlertListener):
    """
    Verifies error handling on closing the NATS connection.
    """
    error = Exception("Close failed")
    listener.nc.close.side_effect = error

    with pytest.raises(Exception) as exc_info:
        await listener.close()

    assert str(exc_info.value) == "Close failed"
    listener.nc.close.assert_called_once()
