#!/bin/bash
# Script to start RabbitMQ for local testing

echo "Starting RabbitMQ for testing..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Using Docker to start RabbitMQ..."
    
    # Start RabbitMQ container
    docker run -d \
        --name rabbitmq-test \
        -p 5672:5672 \
        -p 15672:15672 \
        -e RABBITMQ_DEFAULT_USER=guest \
        -e RABBITMQ_DEFAULT_PASS=guest \
        rabbitmq:3-management
    
    echo "RabbitMQ started on localhost:5672"
    echo "Management UI available at http://localhost:15672 (guest/guest)"
    echo ""
    echo "To stop: docker stop rabbitmq-test && docker rm rabbitmq-test"
    
elif command -v rabbitmq-server &> /dev/null; then
    echo "Starting local RabbitMQ server..."
    rabbitmq-server &
    echo "RabbitMQ started locally"
    
else
    echo "Neither Docker nor RabbitMQ server found."
    echo "Please install Docker or RabbitMQ to run messaging tests."
    echo ""
    echo "Docker installation:"
    echo "  Ubuntu/Debian: sudo apt-get install docker.io"
    echo "  macOS: brew install docker"
    echo ""
    echo "RabbitMQ installation:"
    echo "  Ubuntu/Debian: sudo apt-get install rabbitmq-server"
    echo "  macOS: brew install rabbitmq"
fi
