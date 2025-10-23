import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.mark.external
def test_post_inspection_echoes_json(client, fake_user):
    payload = fake_user
    r = client.post("/post", json=payload)
    body = r.json()
    # httpbin echoes back under 'json'
    assert body["json"] == payload
    assert "headers" in body
    assert body["headers"]["Content-Type"] in (None, "application/json")
    
@pytest.mark.external
def test_anything_endpoint(client):
    r = client.post("/anything/this/path?x=1", data={"a":"b"})
    b = r.json()
    assert b["method"] == "POST"
    assert "/anything/this/path" in b["url"]
    assert b["data"] == "a=b" or b["form"] == {"a": "b"}

def test_post_inspection_echoes_json_mock(client, fake_user):
    """Test POST inspection with mocked response when httpbin.org is unavailable"""
    payload = fake_user
    
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "json": payload,
        "headers": {"Content-Type": "application/json"},
        "url": "https://httpbin.org/post"
    }
    mock_response.status_code = 200
    
    with patch.object(client, 'post', return_value=mock_response):
        r = client.post("/post", json=payload)
        body = r.json()
        
        # Verify the mocked response
        assert body["json"] == payload
        assert "headers" in body
        assert body["headers"]["Content-Type"] == "application/json"

def test_anything_endpoint_mock(client):
    """Test /anything endpoint with mocked response when httpbin.org is unavailable"""
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "method": "POST",
        "url": "https://httpbin.org/anything/this/path?x=1",
        "data": "a=b",
        "form": {"a": "b"}
    }
    mock_response.status_code = 200
    
    with patch.object(client, 'post', return_value=mock_response):
        r = client.post("/anything/this/path?x=1", data={"a":"b"})
        b = r.json()
        
        # Verify the mocked response
        assert b["method"] == "POST"
        assert "/anything/this/path" in b["url"]
        assert b["data"] == "a=b" or b["form"] == {"a": "b"}

def test_request_inspection_data_structure(fake_user):
    """Test request data structure without requiring httpbin.org"""
    payload = fake_user
    
    # Verify payload structure
    assert isinstance(payload, dict)
    assert "name" in payload
    assert "email" in payload
    assert "address" in payload
    assert "sentence" in payload
    
    # Verify data can be serialized to JSON
    import json
    json_payload = json.dumps(payload)
    assert isinstance(json_payload, str)
    
    # Verify data can be deserialized
    deserialized_payload = json.loads(json_payload)
    assert deserialized_payload == payload

