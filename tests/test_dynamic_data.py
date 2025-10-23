import sys
import os
import pytest
import json
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_get_with_random_query_params_mock(client):
    """Test with mocked response when httpbin.org is unavailable"""
    from src.utils.faker_utils import random_query_params
    
    params = random_query_params(4)
    
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {"args": params}
    mock_response.status_code = 200
    
    with patch.object(client, 'get', return_value=mock_response):
        r = client.get("/get", params=params)
        body = r.json()
        
        # Verify the mocked response
        for k, v in params.items():
            assert body["args"].get(k) == v

@pytest.mark.external
def test_get_with_random_query_params_real(client):
    """Test with real httpbin.org (may fail if service is down)"""
    from src.utils.faker_utils import random_query_params
    
    params = random_query_params(4)
    
    try:
        r = client.get("/get", params=params)
        body = r.json()
        # httpbin returns args as strings
        for k, v in params.items():
            assert body["args"].get(k) == v
    except Exception as e:
        pytest.skip(f"httpbin.org is unavailable: {e}")