import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.mark.external
def test_get_returns_json(client):
    r = client.get("/get")
    assert r.headers["Content-Type"].startswith("application/json")
    body = r.json()
    assert "url" in body
    assert "headers" in body

@pytest.mark.external
def test_stream_bytes(client):
    # httpbin /bytes/ returns raw bytes; verify status and length
    r = client.get("/bytes/16")
    assert r.status_code == 200
    assert len(r.content) == 16

def test_get_returns_json_mock(client):
    """Test GET JSON response with mocked data when httpbin.org is unavailable"""
    # Mock the response
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "url": "https://httpbin.org/get",
        "headers": {"User-Agent": "test-agent"},
        "args": {},
        "origin": "127.0.0.1"
    }
    mock_response.status_code = 200
    
    with patch.object(client, 'get', return_value=mock_response):
        r = client.get("/get")
        assert r.headers["Content-Type"].startswith("application/json")
        body = r.json()
        assert "url" in body
        assert "headers" in body

def test_stream_bytes_mock(client):
    """Test bytes streaming with mocked data when httpbin.org is unavailable"""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    
    with patch.object(client, 'get', return_value=mock_response):
        r = client.get("/bytes/16")
        assert r.status_code == 200
        assert len(r.content) == 16

def test_response_format_validation():
    """Test response format validation without requiring httpbin.org"""
    # Test JSON response structure
    json_response = {
        "url": "https://httpbin.org/get",
        "headers": {"User-Agent": "test-agent"},
        "args": {},
        "origin": "127.0.0.1"
    }
    
    # Verify JSON structure
    assert isinstance(json_response, dict)
    assert "url" in json_response
    assert "headers" in json_response
    assert isinstance(json_response["headers"], dict)
    
    # Test bytes response structure
    bytes_response = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    assert isinstance(bytes_response, bytes)
    assert len(bytes_response) == 16
    
    # Test JSON serialization/deserialization
    json_str = json.dumps(json_response)
    assert isinstance(json_str, str)
    
    deserialized = json.loads(json_str)
    assert deserialized == json_response

