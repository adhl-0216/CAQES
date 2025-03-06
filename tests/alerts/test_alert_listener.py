import pytest
from unittest.mock import AsyncMock, patch
import pytest_asyncio
from nats.js.errors import NotFoundError
from alerts.alert_listener import AlertListener, ALERTS_STREAM


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
async def test_try_connect():
    """
    Test the internal _try_connect method
    """
    mock_js = AsyncMock()
    mock_nc = AsyncMock()
    mock_nc.jetstream = AsyncMock(return_value=mock_js)

    with patch('nats.connect', return_value=mock_nc) as mock_connect:
        listener = AlertListener()
        nc, js = await listener._try_connect()

        mock_connect.assert_called_once_with(listener.config.url)
        assert nc == mock_nc
        assert js == mock_js


@pytest.mark.asyncio
async def test_connect_success():
    """
    Test successful connection on first try
    """
    listener = AlertListener()
    mock_nc, mock_js = AsyncMock(), AsyncMock()

    with patch.object(listener, '_try_connect', return_value=(mock_nc, mock_js)) as mock_try:
        await listener.connect()

        mock_try.assert_called_once()
        assert listener.nc == mock_nc
        assert listener.js == mock_js


@pytest.mark.asyncio
async def test_connect_with_retries():
    """
    Test connection with retries before success
    """
    listener = AlertListener()
    mock_nc, mock_js = AsyncMock(), AsyncMock()

    with patch.object(listener, '_try_connect') as mock_try:
        mock_try.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            (mock_nc, mock_js)
        ]

        await listener.connect()

        assert mock_try.call_count == 3
        assert listener.nc == mock_nc
        assert listener.js == mock_js


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


@pytest.mark.asyncio
async def test_start(listener: AlertListener):
    """
    Test successful start of the alert listener
    """
    # Setup mocks
    listener.connect = AsyncMock()
    listener._ensure_streams = AsyncMock()
    listener.js.subscribe = AsyncMock()

    # Execute
    await listener.start()

    # Verify
    listener.connect.assert_not_called()  # Should not connect as js is already set
    listener._ensure_streams.assert_called_once()
    listener.js.subscribe.assert_called_once_with(
        f"{ALERTS_STREAM}.>",
        cb=listener._handle_alert_message
    )


@pytest.mark.asyncio
async def test_start_connection_error(listener: AlertListener):
    """
    Test start method when connection fails
    """
    # Setup
    listener.js = None  # Force connection attempt
    error_msg = "Connection failed"
    listener.connect = AsyncMock(side_effect=Exception(error_msg))

    # Execute and verify
    with pytest.raises(Exception) as exc_info:
        await listener.start()

    assert str(exc_info.value) == error_msg
    listener.connect.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_streams_existing(listener: AlertListener):
    """Test when streams already exist"""
    # Mock stream_info to succeed for both streams
    listener.js.stream_info = AsyncMock()

    await listener._ensure_streams()

    # Should check both streams but not create any
    assert listener.js.stream_info.call_count == 2
    listener.js.add_stream.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_streams_create_new(listener: AlertListener):
    """Test when streams need to be created"""
    # Mock stream_info to fail with NotFoundError
    listener.js.stream_info = AsyncMock(side_effect=NotFoundError)
    listener.js.add_stream = AsyncMock()

    await listener._ensure_streams()

    # Should try to check both streams and create both
    assert listener.js.stream_info.call_count == 2
    assert listener.js.add_stream.call_count == 2


@pytest.mark.asyncio
async def test_ensure_streams_mixed_state(listener: AlertListener):
    """Test when one stream exists and one doesn't"""
    def mock_stream_info(stream_name):
        if stream_name == ALERTS_STREAM:
            return AsyncMock()()
        raise NotFoundError()

    listener.js.stream_info = AsyncMock(side_effect=mock_stream_info)
    listener.js.add_stream = AsyncMock()

    await listener._ensure_streams()

    assert listener.js.stream_info.call_count == 2
    listener.js.add_stream.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_streams_creation_error(listener: AlertListener):
    """Test when stream creation fails"""
    listener.js.stream_info = AsyncMock(side_effect=NotFoundError)
    listener.js.add_stream = AsyncMock(
        side_effect=Exception("Failed to create stream"))

    with pytest.raises(Exception, match="Failed to create stream"):
        await listener._ensure_streams()
