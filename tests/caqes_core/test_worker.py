from mq.client_factory import ClientFactory
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import pytest_asyncio
from settings.worker_settings import WorkerSettings
from caqes_core.worker import Worker


@pytest_asyncio.fixture
async def worker():
    # Create mock settings
    settings = WorkerSettings()

    # Create mock MQ client
    mq_mock = AsyncMock()
    mq_mock.subscribe = AsyncMock()
    mq_mock.close = AsyncMock()

    # Create worker instance
    worker_instance = Worker(settings)
    worker_instance.mq = mq_mock
    
    worker_instance._handle_alert = AsyncMock()

    yield worker_instance

    # Cleanup
    if worker_instance.mq:
        await worker_instance.mq.close()


@pytest.mark.asyncio
async def test_run_successful_execution(worker: Worker):
    """Test normal execution of run method"""
    # Arrange: Mock all async methods
    with patch.object(worker, '_ensure_connected', AsyncMock()) as mock_ensure_connected, patch('asyncio.sleep', AsyncMock(side_effect=[None, asyncio.CancelledError])) as mock_sleep:

        # Act: Run worker.run() directly, expecting it to exit due to mocked sleep raising CancelledError
        try:
            await worker.run()
        except asyncio.CancelledError:
            pass  # Expected due to mock_sleep raising CancelledError

        # Assert
        worker._ensure_connected.assert_awaited_once()
        worker.mq.subscribe.assert_awaited_once_with("alerts", worker._handle_alert)
        assert mock_sleep.await_count == 2  # Called twice: once per loop iteration before raising
        worker.mq.subscribe.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_exception_handling(worker: Worker, capsys):
    """Test error handling in run method"""
    # Arrange
    error = Exception("Test error")
    worker._ensure_connected.side_effect = error

    # Act
    await worker.run()

    # Assert
    captured = capsys.readouterr()
    assert f"Worker error: {error}" in captured.out
    worker._ensure_connected.assert_awaited_once()
    worker.mq.close.assert_awaited_once()
    worker.mq.subscribe.assert_not_awaited()  # Shouldn't reach this point


@pytest.mark.asyncio
async def test_run_mq_cleanup_on_exception(worker: Worker):
    """Test MQ cleanup when exception occurs"""
    # Arrange
    worker._ensure_connected.side_effect = Exception("Test error")

    # Act
    await worker.run()

    # Assert
    worker.mq.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_subscribe_execution(worker: Worker):
    """Test subscription is properly called"""
    # Arrange
    with patch('asyncio.sleep', AsyncMock(side_effect=asyncio.CancelledError)):
        # Run until first sleep
        try:
            await worker.run()
        except asyncio.CancelledError:
            pass

        # Assert
        worker._ensure_connected.assert_awaited_once()
        worker.mq.subscribe.assert_awaited_once_with(
            "alerts", worker._handle_alert)


@pytest.mark.asyncio
async def test_ensure_connected_creates_client_when_none(worker: Worker):
    """Test that a new MQ client is created when none exists"""
    # Arrange
    mock_client = Mock()
    mock_client.is_connected = AsyncMock(
        return_value=False)  # Already connected
    mock_client.connect = AsyncMock()
    worker.mq = None

    with patch.object(ClientFactory, 'create', return_value=mock_client) as mock_create:
        # Act
        await worker._ensure_connected()

        # Assert
        mock_create.assert_called_once_with(worker.settings.mq_client_type)
        assert worker.mq == mock_client
        mock_client.is_connected.assert_awaited_once()
        # Shouldn't need to connect if already connected
        mock_client.connect.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_connected_uses_existing_client(worker: Worker):
    """Test that existing MQ client is used when present"""
    # Arrange
    mock_client = Mock()
    mock_client.is_connected = AsyncMock(return_value=True)
    mock_client.connect = AsyncMock()
    worker.mq = mock_client

    with patch.object(ClientFactory, 'create') as mock_create:
        # Act
        await worker._ensure_connected()

        # Assert
        mock_create.assert_not_called()
        assert worker.mq == mock_client
        mock_client.is_connected.assert_awaited_once()
        mock_client.connect.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_connected_connects_when_not_connected():
    """Test that connect is called when client exists but isn't connected"""
    # Arrange
    worker = Worker()
    mock_client = Mock()
    mock_client.is_connected = AsyncMock(return_value=False)
    mock_client.connect = AsyncMock()
    worker.mq = mock_client

    with patch.object(ClientFactory, 'create') as mock_create:
        # Act
        await worker._ensure_connected()

        # Assert
        mock_create.assert_not_called()
        mock_client.is_connected.assert_awaited_once()
        mock_client.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_connected_handles_connect_failure():
    """Test handling of connection failure"""
    # Arrange
    worker = Worker()
    mock_client = Mock()
    mock_client.is_connected = AsyncMock(return_value=False)
    mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))

    with patch.object(ClientFactory, 'create', return_value=mock_client):
        # Act & Assert
        with pytest.raises(Exception, match="Connection failed"):
            await worker._ensure_connected()

        # Verify steps were attempted
        mock_client.is_connected.assert_awaited_once()
        mock_client.connect.assert_awaited_once()
