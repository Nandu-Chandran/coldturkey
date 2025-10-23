import pytest
import logging
from src.clients.http_client import HTTPBinClient
from src.utils.config import load_config
from src.utils.faker_utils import random_user
from prometheus_client import CollectorRegistry, Counter, generate_latest, start_http_server
import threading

logging.basicConfig(level=logging.INFO)

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

