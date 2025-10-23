# Automation QA Framework

A comprehensive test automation framework for API testing using httpbin.org as the target service.

> ⚠️ **Disclaimer:**  
> The public [httpbin.org](https://httpbin.org) service is often unreliable and may return **503 errors**.  
> To ensure stability, this framework uses a **Dockerized local httpbin container** to simulate the API.  
>  


## Features

- **Configuration Management**: YAML and .env file support
- **Retry Logic**: Custom retry decorator with detailed logging
- **Test Data Generation**: Faker-based utilities for randomized data
- **Reporting**: Allure and HTML reports with automatic generation
- **Messaging Integration**: RabbitMQ support for message queue testing
- **Observability**: Prometheus metrics collection (local development)
- **Dockerized Environment**: Complete docker-compose setup
- **CI/CD Optimized**: Separate configurations for local vs CI environments

## Docker Compose Configurations

### Local Development (`docker-compose.yml`)
- **Full stack**: httpbin, RabbitMQ, Prometheus, Grafana
- **Metrics collection**: Prometheus for observability
- **Visualization**: Grafana dashboards
- **Complete monitoring**: Full observability stack

### CI/CD (`docker-compose.ci.yml`)
- **Minimal stack**: httpbin, RabbitMQ only
- **No metrics**: Excludes Prometheus/Grafana
- **Faster execution**: Optimized for CI performance
- **Resource efficient**: Minimal resource usage

## Project Structure

```
coldturkey/
├── src/
│   ├── clients/
│   │   ├── __init__.py
│   │   └── http_client.py          # HTTP client with retry logic
│   └── utils/
│       ├── __init__.py
│       ├── config.py               # Configuration loader
│       ├── faker_utils.py          # Test data generation
│       └── retry.py                # Retry decorator
├── tests/
│   ├── conftest.py                 # Pytest configuration and fixtures
│   ├── test_config.py              # Configuration tests
│   ├── test_dynamic_data.py        # Dynamic data tests
│   ├── test_messaging_rabbitmq.py  # RabbitMQ tests
│   ├── test_request_inspection.py  # Request inspection tests
│   └── test_response_formats.py    # Response format tests
├── config.yaml                     # Main configuration
├── docker-compose.yml              # Docker services
├── prometheus.yml                  # Prometheus configuration
├── pytest.ini                     # Pytest configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Setup

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for bonus features)
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coldturkey
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Tests

#### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_response_formats.py

# Run tests with specific markers
pytest -m "not external"  # Skip external service tests
pytest -m external        # Run only external service tests
```

#### Test Categories

- **Unit Tests**: Fast, isolated tests (`@pytest.mark.unit`)
- **Integration Tests**: Tests with dependencies (`@pytest.mark.integration`)
- **External Tests**: Tests requiring external services (`@pytest.mark.external`)
- **Mock Tests**: Tests using mocked responses (no external dependencies)

#### Handling Service Outages

The framework automatically handles external service outages:

1. **httpbin.org Outages**: 
   - External tests are automatically skipped
   - Mock tests continue to run
   - Data structure validation tests always run

2. **RabbitMQ Unavailable**:
   - RabbitMQ tests are automatically skipped
   - Mock messaging tests continue to run
   - Message structure validation tests always run

#### Running Tests During Outages

```bash
# Run all tests (will skip external tests if services are down)
pytest -v

# Run only mock tests (no external dependencies)
pytest -m "not external"

# Run only unit tests (fastest, no external dependencies)
pytest -m unit

# Run specific test categories
pytest tests/test_response_formats.py::test_get_returns_json_mock
pytest tests/test_request_inspection.py::test_post_inspection_echoes_json_mock
pytest tests/test_messaging_rabbitmq.py::test_publish_and_consume_rabbitmq_mock
```

#### Mock Tests

When httpbin.org is unavailable, the framework automatically:
- Skips external tests
- Provides mock-based alternatives
- Continues execution with available tests

> Created a configurable variable, that default to 'internal' httpbin service for testing.

### Reporting

#### Allure Reports

```bash
# Generate Allure results
pytest --alluredir=allure-results

# Serve Allure report (requires Allure CLI)
allure serve allure-results

# Generate static report
allure generate allure-results --clean -o allure-report
```

#### HTML Reports

```bash
# Generate HTML report
pytest --html=report.html --self-contained-html
```

## Docker Setup (Recommended)

The entire test framework can be run using Docker with all services containerized.

### Prerequisites

- Docker and Docker Compose
- Make (optional, for easier commands)

### Quick Start with Docker

```bash
# Clone and navigate to the project
git clone <repository-url>
cd coldturkey

# Start all services and run tests
make test

# Or using docker-compose directly
docker-compose up -d
docker-compose run --rm test-framework
```

### Docker Services

The Docker setup includes:

- **httpbin**: Local API service (alternative to httpbin.org)
- **RabbitMQ**: Message broker with management UI
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Test Framework**: Containerized test runner

### Docker Commands

#### Using Make (Recommended)

```bash
# Start all services
make start

# Run all tests
make test

# Run mock tests only (no external dependencies)
make test-mock

# Run external service tests
make test-external

# Run unit tests only
make test-unit

# Show service URLs
make urls

# Generate reports
make reports

# Stop all services
make stop

# Clean up everything
make cleanup
```

#### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Run all tests
docker-compose run --rm test-framework

# Run mock tests only
docker-compose run --rm test-runner-mock

# Run external service tests
docker-compose run --rm test-runner-external

# Show logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Using the Test Runner Script

```bash
# Make script executable
chmod +x scripts/docker-test-runner.sh

# Start services
./scripts/docker-test-runner.sh start

# Run tests
./scripts/docker-test-runner.sh test

# Run specific test types
./scripts/docker-test-runner.sh test mock
./scripts/docker-test-runner.sh test external
./scripts/docker-test-runner.sh test unit

# Show service URLs
./scripts/docker-test-runner.sh urls

# Generate reports
./scripts/docker-test-runner.sh reports

# Stop services
./scripts/docker-test-runner.sh stop
```

### Service URLs

When running with Docker, services are available at:

- **httpbin**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Test Reports**: ./reports/
- **Allure Reports**: ./allure-report/

### Docker Environment Variables

The framework automatically detects Docker environment and uses:

- `HTTPBIN_URL=http://httpbin:80` (internal Docker network)
- `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/` (internal Docker network)
- `PROMETHEUS_URL=http://prometheus:9090` (internal Docker network)

### Docker Volumes

The following directories are mounted as volumes:

- `./allure-results` - Allure test results
- `./allure-report` - Generated Allure reports
- `./reports` - HTML test reports

### Development with Docker

```bash
# Start services in development mode
make dev

# Run tests multiple times
make test
make test-mock
make test-external

# View logs
make logs

# Stop when done
make stop
```

### Troubleshooting Docker

#### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :8080,5672,15672,9090,3000
   
   # Stop conflicting services
   docker-compose down
   ```

2. **Services Not Starting**
   ```bash
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs httpbin
   docker-compose logs rabbitmq
   ```

3. **Test Failures**
   ```bash
   # Run mock tests only
   make test-mock
   
   # Check test logs
   docker-compose logs test-framework
   ```

4. **Clean Start**
   ```bash
   # Clean everything and start fresh
   make cleanup
   make start
   make test
   ```

#### Docker Performance

For better performance on macOS/Windows:

```bash
# Increase Docker memory allocation
# Docker Desktop -> Settings -> Resources -> Memory: 4GB+

# Use Docker BuildKit
export DOCKER_BUILDKIT=1
```

### CI/CD with Docker

#### GitHub Actions Example

```yaml
name: Docker Test Framework
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      - name: Build and test
        run: |
          docker-compose build
          docker-compose run --rm test-framework
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: allure-results/
```

### Docker Production Deployment

For production deployment:

```bash
# Build production image
docker build -t test-framework:latest .

# Run with production configuration
docker run -d \
  --name test-framework \
  -v ./reports:/app/reports \
  -e ENV=production \
  test-framework:latest
```

#### Start All Services

```bash
# Start all services (API, RabbitMQ, Prometheus, Grafana)
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

#### Services Included

- **httpbin.org**: API under test (via external service)
- **RabbitMQ**: Message broker for messaging tests
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

#### Access Services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- RabbitMQ Management: http://localhost:15672 (guest/guest)

### Configuration

#### Main Configuration (`config.yaml`)

```yaml
base_url: "https://httpbin.org"
timeout: 10
retry:
  attempts: 5
  backoff_seconds: 2
rabbitmq:
  url: "amqp://guest:guest@localhost:5672/"
  queue: "test_queue"
metrics:
  port: 8001
```

#### Environment Variables (`.env`)

```bash
ENV=local
HTTPBIN_URL=https://httpbin.org
TIMEOUT=10
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

#### RabbitMQ Tests

The framework includes three types of RabbitMQ tests:

1. **Real RabbitMQ Test** (`test_publish_and_consume_rabbitmq`):
   - Requires RabbitMQ server to be running
   - Tests actual message publishing and consumption
   - Automatically skipped if RabbitMQ is not available

2. **Mock RabbitMQ Test** (`test_publish_and_consume_rabbitmq_mock`):
   - Uses mocked RabbitMQ connection
   - Tests the same logic without requiring RabbitMQ
   - Always runs regardless of RabbitMQ availability

3. **Message Structure Test** (`test_rabbitmq_message_structure`):
   - Tests message format and encoding/decoding
   - No RabbitMQ connection required
   - Validates data structure and serialization

#### Running RabbitMQ Tests

```bash
# Run all RabbitMQ tests (real + mock + structure)
pytest tests/test_messaging_rabbitmq.py

# Run only mock tests (no RabbitMQ required)
pytest tests/test_messaging_rabbitmq.py::test_publish_and_consume_rabbitmq_mock
pytest tests/test_messaging_rabbitmq.py::test_rabbitmq_message_structure

# Run only real RabbitMQ tests (requires RabbitMQ)
pytest tests/test_messaging_rabbitmq.py::test_publish_and_consume_rabbitmq

# Skip RabbitMQ tests entirely
pytest -m "not rabbitmq"
```

#### Starting RabbitMQ for Real Tests

If you want to run the real RabbitMQ tests, you can start RabbitMQ using Docker:

```bash
# Start RabbitMQ with Docker
docker run -d \
  --name rabbitmq-test \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3-management

# Run the real RabbitMQ test
pytest tests/test_messaging_rabbitmq.py::test_publish_and_consume_rabbitmq

# Stop RabbitMQ when done
docker stop rabbitmq-test && docker rm rabbitmq-test
```

The management UI will be available at http://localhost:15672 (guest/guest).

#### Retry Logic

The framework includes a custom retry decorator with:
- Configurable attempts and backoff
- Detailed logging for each attempt
- Exception-specific retry policies
- Exponential backoff support

```python
@retry(attempts=3, backoff_seconds=2, allowed_exceptions=(requests.RequestException,))
def api_call(self):
    # API call implementation
    pass
```

#### Test Data Generation

Faker-based utilities for generating realistic test data:

```python
from src.utils.faker_utils import random_user, random_query_params

# Generate random user data
user = random_user()
# {'name': 'John Doe', 'email': 'john@example.com', ...}

# Generate random query parameters
params = random_query_params(5)
# {'param1': 'value1', 'param2': 'value2', ...}
```

#### Metrics Collection

Prometheus metrics for test observability:
- Test execution duration
- Retry attempt counts
- Success/failure rates
- Custom business metrics

### CI/CD Integration

#### GitHub Actions Example

```yaml
name: Test Framework
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --alluredir=allure-results
      - name: Upload Allure results
        uses: actions/upload-artifact@v2
        with:
          name: allure-results
          path: allure-results
```

### Troubleshooting

#### Common Issues

1. **Import Errors**
   - Ensure Python path is correctly configured
   - Check that all `__init__.py` files exist
   - Verify pytest.ini configuration

2. **503 Service Unavailable**
   - Framework automatically handles httpbin.org outages
   - Use mock tests when external services are down
   - Check network connectivity

3. **Docker Issues**
   - Ensure Docker is running
   - Check port conflicts
   - Verify docker-compose.yml configuration

#### Debug Mode

```bash
# Enable debug logging
pytest -v -s --log-cli-level=DEBUG

# Run single test with detailed output
pytest -v -s tests/test_response_formats.py::test_get_returns_json
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### License

This project is licensed under the MIT License.
