#!/bin/bash
# Docker-based test runner script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p allure-results allure-report reports
}

# Function to start services
start_services() {
    print_status "Starting all services..."
    docker-compose up -d httpbin rabbitmq prometheus grafana
    
    print_status "Waiting for services to be healthy..."
    docker-compose ps
    
    # Wait for services to be ready
    print_status "Waiting for httpbin to be ready..."
    until curl -f http://localhost:8080/get > /dev/null 2>&1; do
        sleep 2
    done
    
    print_status "Waiting for RabbitMQ to be ready..."
    until docker-compose exec rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; do
        sleep 2
    done
    
    print_success "All services are ready!"
}

# Function to run tests
run_tests() {
    local test_type=${1:-"all"}
    
    case $test_type in
        "all")
            print_status "Running all tests..."
            docker-compose run --rm test-framework
            ;;
        "mock")
            print_status "Running mock tests only..."
            docker-compose run --rm test-runner-mock
            ;;
        "external")
            print_status "Running external service tests..."
            docker-compose run --rm test-runner-external
            ;;
        "unit")
            print_status "Running unit tests..."
            docker-compose run --rm test-framework pytest -v -m unit
            ;;
        *)
            print_error "Invalid test type: $test_type"
            print_status "Valid options: all, mock, external, unit"
            exit 1
            ;;
    esac
}

# Function to generate reports
generate_reports() {
    print_status "Generating Allure report..."
    docker-compose run --rm test-framework allure generate allure-results --clean -o allure-report
    
    print_success "Reports generated in allure-report/ and reports/ directories"
}

# Function to show service URLs
show_urls() {
    print_status "Service URLs:"
    echo "  httpbin:      http://localhost:8080"
    echo "  RabbitMQ:     http://localhost:15672 (guest/guest)"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3000 (admin/admin)"
    echo "  Test Reports: ./reports/"
    echo "  Allure:       ./allure-report/"
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show logs
show_logs() {
    local service=${1:-"all"}
    if [ "$service" = "all" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  test        Run tests [all|mock|external|unit]"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs [service_name]"
    echo "  urls        Show service URLs"
    echo "  reports     Generate test reports"
    echo "  cleanup     Clean up everything"
    echo "  help        Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 test mock                # Run mock tests only"
    echo "  $0 test external            # Run external service tests"
    echo "  $0 logs test-framework      # Show test framework logs"
    echo "  $0 reports                  # Generate Allure reports"
}

# Main script logic
main() {
    check_docker
    create_directories
    
    case ${1:-"help"} in
        "start")
            start_services
            show_urls
            ;;
        "test")
            start_services
            run_tests "$2"
            generate_reports
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            show_urls
            ;;
        "logs")
            show_logs "$2"
            ;;
        "urls")
            show_urls
            ;;
        "reports")
            generate_reports
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
