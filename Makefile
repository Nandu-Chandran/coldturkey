# Makefile for Docker-based test automation framework

.PHONY: help build start stop restart test test-mock test-external test-unit logs urls reports cleanup

# Default target
help:
	@echo "Available commands:"
	@echo "  make build          - Build the test framework Docker image"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make test           - Run all tests"
	@echo "  make test-mock      - Run mock tests only"
	@echo "  make test-external  - Run external service tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make logs           - Show logs for all services"
	@echo "  make urls           - Show service URLs"
	@echo "  make reports        - Generate test reports"
	@echo "  make cleanup        - Clean up everything"

# Build the Docker image
build:
	@echo "Building test framework Docker image..."
	docker compose build test-framework

# Start all services
start:
	@echo "Starting all services..."
	docker compose up -d httpbin rabbitmq prometheus grafana
	@echo "Waiting for services to be ready..."
	@until curl -f http://localhost:8080/get > /dev/null 2>&1; do sleep 2; done
	@until docker compose exec rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; do sleep 2; done
	@echo "All services are ready!"

# Stop all services
stop:
	@echo "Stopping all services..."
	docker compose down

# Restart all services
restart: stop start

# Run all tests
test: start
	@echo "Running all tests..."
	docker compose run --rm test-framework
	@make reports

# Run mock tests only
test-mock:
	@echo "Running mock tests..."
	docker compose run --rm test-runner-mock
	@make reports

# Run external service tests
test-external: start
	@echo "Running external service tests..."
	docker compose run --rm test-runner-external
	@make reports

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	docker compose run --rm test-framework pytest -v -m unit
	@make reports

# Show logs
logs:
	@echo "Showing logs for all services..."
	docker compose logs -f

# Show service URLs
urls:
	@echo "Service URLs:"
	@echo "  httpbin:      http://localhost:8080"
	@echo "  RabbitMQ:     http://localhost:15672 (guest/guest)"
	@echo "  Prometheus:   http://localhost:9090"
	@echo "  Grafana:      http://localhost:3000 (admin/admin)"
	@echo "  Test Reports: ./reports/"
	@echo "  Allure:       ./allure-report/"

# Generate reports
reports:
	@echo "Generating Allure report..."
	@mkdir -p allure-results allure-report reports
	docker compose run --rm test-framework allure generate allure-results --clean -o allure-report
	@echo "Reports generated in allure-report/ and reports/ directories"

# Clean up everything
cleanup:
	@echo "Cleaning up..."
	docker compose down -v
	docker system prune -f
	@echo "Cleanup completed"

# Quick test (mock only, no services needed)
quick-test:
	@echo "Running quick mock tests..."
	docker compose run --rm test-runner-mock

# Development mode (start services and keep them running)
dev: start
	@echo "Development mode: Services are running"
	@echo "Use 'make test' to run tests"
	@echo "Use 'make stop' to stop services"
	@make urls
