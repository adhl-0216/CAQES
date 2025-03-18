import pytest

from datetime import datetime
from unittest.mock import MagicMock
from pytest_httpserver.httpserver import HTTPServer
from http import HTTPStatus
from werkzeug import Request, Response

from quarantine.protocol.emqx_quarantine import EMQXQuarantine

# Fixtures
@pytest.fixture
def emqx_module(httpserver: HTTPServer)-> EMQXQuarantine:
    return EMQXQuarantine(
        base_url=httpserver.url_for("/api/v5"),
        api_key="test_key",
        api_secret="test_secret"
    )

@pytest.fixture
def mock_emqx_server(httpserver: HTTPServer):
    return httpserver

# Test Cases
def test_ban_by_clientid_success_with_method_mock(mock_emqx_server: HTTPServer, emqx_module: EMQXQuarantine):
    """Test banning a client by Client ID with a mocked _get_client_id_by_ip."""
    # Arrange: Mock _get_client_id_by_ip to return a client ID
    emqx_module._get_client_id_by_ip = MagicMock(return_value="iot-device-123")
    
    # Arrange: Mock a successful POST to /banned with a custom matcher
    def handler(request: Request):
        try:
            payload = request.json
            expected = {
                "as": "clientid",
                "who": "iot-device-123",
                "reason": "Suspicious activity"
            }
            # Check if expected fields match and required dynamic fields are present
            if (all(payload.get(k) == v for k, v in expected.items()) and
                            "by" in payload and
                            "at" in payload):
                        return Response('{}', status=HTTPStatus.OK, mimetype='application/json')
            raise Exception("Mismatch")
        except Exception as e:
            return Response('{"error": "Request did not match expected payload"}', 
                            status=HTTPStatus.BAD_REQUEST, 
                            mimetype='application/json')

    mock_emqx_server.expect_request(
        "/api/v5/banned",
        method="POST"
    ).respond_with_handler(handler)

    # Act: Ban the client by IP address
    result = emqx_module.ban(
        ip_address="192.168.0.12",
        reason="Suspicious activity"
    )

    # Assert: Check success
    assert result is True
    assert len(mock_emqx_server.log) == 1  # Only one request: POST /banned

def test_ban_by_ip_success(mock_emqx_server: HTTPServer, emqx_module: EMQXQuarantine):
    """Test banning a client by IP with a successful API response."""
    # Arrange: Mock _get_client_id_by_ip to raise an exception, triggering IP fallback
    emqx_module._get_client_id_by_ip = MagicMock(side_effect=Exception("Client Not Found"))

    # Arrange: Mock a successful POST to /banned with a custom handler
    def handler(request: Request):
        try:
            payload = request.json
            expected = {
                "as": "peerhost",
                "who": "192.168.10.50",
                "reason": "Suspicious traffic"
            }
            if (all(payload.get(k) == v for k, v in expected.items()) and
                    "by" in payload and
                    "at" in payload):
                return Response('{}', status=HTTPStatus.OK, mimetype='application/json')
            raise Exception("Mismatch")
        except Exception:
            return Response('{"error": "Request did not match expected payload"}', 
                            status=HTTPStatus.BAD_REQUEST, 
                            mimetype='application/json')

    mock_emqx_server.expect_request(
        "/api/v5/banned",
        method="POST"
    ).respond_with_handler(handler)

    # Act: Ban the IP
    result = emqx_module.ban(
        ip_address="192.168.10.50",
        reason="Suspicious traffic"
    )

    # Assert: Check success
    assert result is True
    assert len(mock_emqx_server.log) == 1  # Only one request: POST /banned

def test_ban_with_expiration(mock_emqx_server: HTTPServer, emqx_module: EMQXQuarantine):
    """Test banning a client with an expire_at timestamp."""
    # Arrange: Mock _get_client_id_by_ip to return a client ID
    emqx_module._get_client_id_by_ip = MagicMock(return_value="iot-device-123")
    
    # Arrange: Mock a successful POST to /banned with a custom matcher
    def handler(request: Request):
        try:
            payload = request.json
            expected = {
                "as": "clientid",
                "who": "iot-device-123",
                "reason": "Suspicious activity"
            }
            
            # Check if expected fields match and required dynamic fields are present
            if (all(payload.get(k) == v for k, v in expected.items()) and
                            "by" in payload and
                            "at" in payload and
                            "until" in payload):
                        return Response('{}', status=HTTPStatus.OK, mimetype='application/json')
            raise Exception("Mismatch")
        except Exception as e:
            return Response('{"error": "Request did not match expected payload"}', 
                            status=HTTPStatus.BAD_REQUEST, 
                            mimetype='application/json')

    mock_emqx_server.expect_request(
        "/api/v5/banned",
        method="POST"
    ).respond_with_handler(handler)

    # Act: Ban the client by IP address
    result = emqx_module.ban(
        ip_address="192.168.0.12",
        reason="Suspicious activity",
        expire_at=datetime.now().isoformat()
    )

    # Assert: Check success
    assert result is True
    assert len(mock_emqx_server.log) == 1  # Only one request: POST /banned

def test_ban_error(mock_emqx_server: HTTPServer, emqx_module: EMQXQuarantine):
    """Test ban handles network errors (e.g., timeout) gracefully."""
    # Arrange: Mock _get_client_id_by_ip to return a client ID
    emqx_module._get_client_id_by_ip = MagicMock(return_value="iot-device-123")

    mock_emqx_server.expect_request(
        "/api/v5/banned",
        method="POST"
    ).respond_with_response(Response(status=HTTPStatus.INTERNAL_SERVER_ERROR))

    # Act: Ban the client by IP address
    with pytest.raises(Exception) as ex:
        emqx_module.ban(
        ip_address="192.168.0.12",
        reason="Suspicious activity"
    )
        
    # Assert: Exception raised
    assert "Response NOT OK" in str(ex.value)
    
# test unban
# def test_unban_by_clientid_success(mock_emqx_server, emqx_module):
#     """Test unbanning a client by Client ID with a successful response."""

# def test_unban_by_ip_success(mock_emqx_server, emqx_module):
#     """Test unbanning a client by IP with a successful response."""

# def test_unban_invalid_identifier_type(emqx_module):
#     """Test unban fails with an unsupported identifier_type."""

# def test_unban_nonexistent_client(mock_emqx_server, emqx_module):
#     """Test unbanning a client that isn’t banned (e.g., 404 response)."""

# def test_unban_network_failure(mock_emqx_server, emqx_module):
#     """Test unban handles network errors gracefully."""

# test is_banned
# def test_is_banned_clientid_true(mock_emqx_server, emqx_module):
#     """Test is_banned returns True for a banned Client ID."""

# def test_is_banned_ip_true(mock_emqx_server, emqx_module):
#     """Test is_banned returns True for a banned IP."""

# def test_is_banned_not_banned(mock_emqx_server, emqx_module):
#     """Test is_banned returns False for an unbanned identifier."""

# def test_is_banned_invalid_identifier_type(emqx_module):
#     """Test is_banned fails with an unsupported identifier_type."""

# def test_is_banned_network_failure(mock_emqx_server, emqx_module):
#     """Test is_banned handles network errors gracefully."""

# def test_is_banned_empty_blacklist(mock_emqx_server, emqx_module):
#     """Test is_banned returns False when the blacklist is empty."""

# edge cases
# def test_ban_and_unban_full_cycle(mock_emqx_server, emqx_module):
#     """Test a full ban → is_banned → unban → is_banned cycle."""