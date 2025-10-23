import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import load_config
from src.utils.faker_utils import random_user, random_query_params
from src.clients.http_client import HTTPBinClient


@pytest.mark.unit
def test_config_loading():
    """Test configuration loading without external dependencies"""
    config = load_config()
    
    # Test that config has required keys
    assert 'base_url' in config
    assert 'timeout' in config
    assert 'retry' in config
    assert 'rabbitmq' in config
    
    # Test config values
    assert isinstance(config['timeout'], int)
    assert config['timeout'] > 0
    assert isinstance(config['retry']['attempts'], int)
    assert config['retry']['attempts'] > 0


@pytest.mark.unit
def test_faker_utils():
    """Test faker utilities without external dependencies"""
    # Test random user generation
    user = random_user()
    assert isinstance(user, dict)
    assert 'name' in user
    assert 'email' in user
    assert isinstance(user['name'], str)
    assert isinstance(user['email'], str)
    
    # Test random query params
    params = random_query_params(3)
    assert isinstance(params, dict)
    assert len(params) <= 3
    for key, value in params.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


@pytest.mark.unit
def test_http_client_initialization():
    """Test HTTP client initialization without external dependencies"""
    client = HTTPBinClient(base_url="http://test:80", timeout=5)
    
    assert client.base_url == "http://test:80"
    assert client.timeout == 5


@pytest.mark.unit
def test_http_client_get_method():
    """Test HTTP client GET method with mocked response"""
    client = HTTPBinClient(base_url="http://test:80", timeout=5)
    
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        response = client.get("/test")
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        assert response.status_code == 200
        assert response.json() == {"test": "data"}


@pytest.mark.unit
def test_http_client_post_method():
    """Test HTTP client POST method with mocked response"""
    client = HTTPBinClient(base_url="http://test:80", timeout=5)
    
    # Mock the requests.post call
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"created": True}
    
    test_data = {"key": "value"}
    
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.post("/test", json=test_data)
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        assert response.status_code == 201
        assert response.json() == {"created": True}


@pytest.mark.unit
def test_retry_decorator():
    """Test retry decorator functionality"""
    from src.utils.retry import retry
    
    call_count = 0
    
    @retry(attempts=3, backoff_seconds=0.1, allowed_exceptions=(ValueError,))
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 3


@pytest.mark.unit
def test_retry_decorator_max_attempts():
    """Test retry decorator with max attempts reached"""
    from src.utils.retry import retry
    
    call_count = 0
    
    @retry(attempts=2, backoff_seconds=0.1, allowed_exceptions=(ValueError,))
    def always_failing_function():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        always_failing_function()
    
    assert call_count == 2


@pytest.mark.unit
def test_message_structure():
    """Test message structure without requiring RabbitMQ"""
    import uuid
    
    # Test message creation
    corr_id = str(uuid.uuid4())
    message = {"hello": "world", "id": corr_id}
    message_body = str(message)
    
    # Verify message structure
    assert "hello" in message
    assert "id" in message
    assert message["id"] == corr_id
    assert isinstance(message_body, str)
    
    # Verify message can be encoded/decoded
    encoded_body = message_body.encode()
    decoded_body = encoded_body.decode()
    assert decoded_body == message_body
    assert corr_id in decoded_body


@pytest.mark.unit
def test_config_environment_variables():
    """Test configuration with environment variables"""
    import os
    
    # Set test environment variables
    os.environ['HTTPBIN_URL'] = 'http://test-env:80'
    os.environ['RABBITMQ_URL'] = 'amqp://test:test@test:5672/'
    os.environ['PROMETHEUS_URL'] = 'http://test-prometheus:9090'
    
    try:
        config = load_config()
        
        # Test that environment variables are loaded
        assert config.get('httpbin_url') == 'http://test-env:80'
        assert config.get('rabbitmq_url') == 'amqp://test:test@test:5672/'
        assert config.get('prometheus_url') == 'http://test-prometheus:9090'
    finally:
        # Clean up environment variables
        for key in ['HTTPBIN_URL', 'RABBITMQ_URL', 'PROMETHEUS_URL']:
            if key in os.environ:
                del os.environ[key]
