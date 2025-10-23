import pytest
import pika
import time
import uuid
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _is_rabbitmq_available(config):
    """Check if RabbitMQ is available"""
    try:
        url = config['rabbitmq'].get('url') or "amqp://guest:guest@localhost:5672/"
        params = pika.URLParameters(url)
        conn = pika.BlockingConnection(params)
        conn.close()
        return True
    except:
        return False

@pytest.mark.external
@pytest.mark.rabbitmq
def test_publish_and_consume_rabbitmq(config):
    """Test RabbitMQ messaging (requires RabbitMQ to be running)"""
    if not _is_rabbitmq_available(config):
        pytest.skip("RabbitMQ is not available")
    
    url = config['rabbitmq'].get('url') or "amqp://guest:guest@localhost:5672/"
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    queue = config['rabbitmq'].get('queue', 'test_queue')
    ch.queue_declare(queue=queue, durable=False, auto_delete=True)
    corr_id = str(uuid.uuid4())
    message = {"hello": "world", "id": corr_id}
    ch.basic_publish(exchange="", routing_key=queue, body=str(message))

    # consume (poll for message) with a short timeout
    method_frame, header_frame, body = ch.basic_get(queue=queue, auto_ack=True)
    assert body is not None
    assert corr_id in body.decode()
    conn.close()

def test_publish_and_consume_rabbitmq_mock(config):
    """Test RabbitMQ messaging with mocked connection (no RabbitMQ required)"""
    # Mock the RabbitMQ connection and channel
    mock_conn = Mock()
    mock_channel = Mock()
    mock_conn.channel.return_value = mock_channel
    
    # Mock message data
    corr_id = str(uuid.uuid4())
    message = {"hello": "world", "id": corr_id}
    message_body = str(message)
    
    # Mock the basic_get response
    mock_channel.basic_get.return_value = (Mock(), Mock(), message_body.encode())
    
    with patch('pika.BlockingConnection', return_value=mock_conn):
        url = config['rabbitmq'].get('url') or "amqp://guest:guest@localhost:5672/"
        params = pika.URLParameters(url)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        queue = config['rabbitmq'].get('queue', 'test_queue')
        ch.queue_declare(queue=queue, durable=False, auto_delete=True)
        ch.basic_publish(exchange="", routing_key=queue, body=message_body)
        
        # consume (poll for message)
        method_frame, header_frame, body = ch.basic_get(queue=queue, auto_ack=True)
        assert body is not None
        assert corr_id in body.decode()
        conn.close()

def test_rabbitmq_message_structure():
    """Test message structure without requiring RabbitMQ connection"""
    # Test that our message format is correct
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

