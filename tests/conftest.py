import pytest
import logging
import sys
import os
import requests

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.http_client import HTTPBinClient
from src.utils.config import load_config
from src.utils.faker_utils import random_user

from prometheus_client import CollectorRegistry, Counter, generate_latest, start_http_server
import threading

logging.basicConfig(level=logging.INFO)

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "external: mark test as requiring external service")
    config.addinivalue_line("markers", "rabbitmq: mark test as requiring RabbitMQ")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip external tests if service is unavailable"""
    for item in items:
        if "external" in item.keywords:
            item.add_marker(pytest.mark.skipif(
                not _is_httpbin_available(),
                reason="httpbin.org is not available"
            ))
        if "rabbitmq" in item.keywords:
            item.add_marker(pytest.mark.skipif(
                not _is_rabbitmq_available(),
                reason="RabbitMQ is not available"
            ))

def _is_httpbin_available():
    """Check if httpbin service is available based on configuration"""
    try:
        config = load_config()
        ext_http = config.get('ext_http', 0)
        
        if ext_http == 1:
            # Check external httpbin.org
            response = requests.get("https://httpbin.org/get", timeout=5)
            return response.status_code == 200
        else:
            # Check internal containerized httpbin
            base_url = config.get('base_url', 'http://httpbin:80')
            response = requests.get(f"{base_url}/get", timeout=5)
            return response.status_code == 200
    except:
        return False

def _is_rabbitmq_available():
    """Check if RabbitMQ is available"""
    try:
        import pika
        import time
        
        # Check if RabbitMQ tests should be skipped
        config = load_config()
        skip_rabbitmq = config.get('skip_rabbitmq', 0)
        if skip_rabbitmq == 1:
            print("RabbitMQ tests are disabled by configuration")
            return False
        
        # Try Docker RabbitMQ first, then localhost
        urls = [
            "amqp://guest:guest@rabbitmq:5672/",  # Docker service name
            "amqp://guest:guest@localhost:5672/"  # Localhost fallback
        ]
        
        # Try each URL with retries for CI environments
        for url in urls:
            for attempt in range(3):  # Try up to 3 times
                try:
                    params = pika.URLParameters(url)
                    # Set shorter timeout for CI
                    params.connection_attempts = 1
                    params.retry_delay = 1
                    conn = pika.BlockingConnection(params)
                    conn.close()
                    print(f"RabbitMQ connection successful: {url}")
                    return True
                except Exception as e:
                    print(f"RabbitMQ connection attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(2)
                    continue
        print("All RabbitMQ connection attempts failed")
        return False
    except Exception as e:
        print(f"RabbitMQ availability check failed: {e}")
        return False

@pytest.fixture(scope="session")
def config():
    return load_config()

@pytest.fixture(scope="session")
def client(config):
    return HTTPBinClient(base_url=config['base_url'], timeout=config['timeout'])

@pytest.fixture
def fake_user():
    return random_user()

# optional: metrics server for tests (bonus)
@pytest.fixture(scope="session", autouse=False)
def prometheus_server(config):
    # Expose a tiny metrics server for Prometheus to scrape
    registry = CollectorRegistry()
    retries_counter = Counter("test_retries_total", "Total retries", registry=registry)
    # start a thread server
    port = config.get("metrics", {}).get("port", 8001)
    t = threading.Thread(target=lambda: start_http_server(port, registry=registry), daemon=True)
    t.start()
    yield {"registry": registry, "retries_counter": retries_counter}

