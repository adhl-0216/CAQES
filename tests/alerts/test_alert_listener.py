import pytest
from unittest.mock import AsyncMock, patch
import pytest_asyncio

from alerts.alert_listener import AlertListener

pytest_plugins = ['pytest_asyncio']


@pytest_asyncio.fixture
async def listener() -> AlertListener:
    """
    Fixture that creates a mock AlertListener instance with mocked NATS connection.
    """
    listener = AlertListener()
    listener.nc = AsyncMock()
    return listener


@pytest.mark.asyncio
@patch('nats.connect')
async def test_connect(mock_connect):
    """
    Verifies that the NATS connection is established with correct URL
    """
    mock_connect.return_value = AsyncMock()

    listener = AlertListener()
    await listener.connect()

    mock_connect.assert_called_once_with("nats://nats:4222")


@pytest.mark.asyncio
async def test_close(listener: AlertListener):
    """
    Test the proper cleanup of NATS connection.
    Verifies that the NATS connection is closed when the listener is terminated.
    """
    await listener.close()

    listener.nc.close.assert_called_once()
