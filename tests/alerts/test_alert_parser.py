import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from alerts.alert_parser import AlertParser
from models import AlertJob


@pytest.fixture
async def alert_parser():
    parser = AlertParser()
    parser.nc = AsyncMock()
    parser.js = AsyncMock()
    return parser


@pytest.mark.asyncio
async def test_connect():
    parser = AlertParser()
    with patch('nats.connect') as mock_connect:
        mock_js = AsyncMock()
        mock_connect.return_value = AsyncMock(
            jetstream=MagicMock(return_value=mock_js))
        await parser.connect()
        mock_connect.assert_called_once_with("nats://nats:4222")
        assert parser.nc is not None
        assert parser.js is not None


@pytest.mark.asyncio
async def test_start_worker(alert_parser):
    mock_msg = AsyncMock()
    mock_msg.data = json.dumps({
        "job_id": "test-id",
        "alert_data": {"type": "test", "message": "test alert"},
        "status": "pending"
    }).encode()

    # Test successful job processing
    await alert_parser.js.subscribe.return_value(mock_msg)
    mock_msg.ack.assert_called_once()

    # Test failed job processing
    mock_msg.reset_mock()
    mock_msg.data = b"invalid json"
    await alert_parser.js.subscribe.return_value(mock_msg)
    mock_msg.nak.assert_called_once()
