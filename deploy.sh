#!/bin/bash

# Attack Surface Scanner Deployment Script

set -e

echo "🚀 Attack Surface Scanner Deployment"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to build and run the application
deploy() {
    echo "📦 Building Docker image..."
    docker-compose build
    
    echo "🔧 Starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Health check
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Attack Surface Scanner is running successfully!"
        echo "🌐 Access the application at: http://localhost:5000"
        echo ""
        echo "📊 To view logs: docker-compose logs -f"
        echo "🛑 To stop: docker-compose down"
    else
        echo "❌ Health check failed. Check the logs:"
        docker-compose logs
        exit 1
    fi
}

# Function to stop the application
stop() {
    echo "🛑 Stopping Attack Surface Scanner..."
    docker-compose down
    echo "✅ Services stopped successfully!"
}

# Function to view logs
logs() {
    echo "📊 Viewing logs (Press Ctrl+C to exit)..."
    docker-compose logs -f
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup completed!"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        stop
        ;;
    "logs")
        logs
        ;;
    "cleanup")
        cleanup
        ;;
    "restart")
        stop
        deploy
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs|cleanup|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Build and start the application (default)"
        echo "  stop     - Stop the application"
        echo "  logs     - View application logs"
        echo "  cleanup  - Stop and remove all containers and volumes"
        echo "  restart  - Stop and restart the application"
        exit 1
        ;;
esac