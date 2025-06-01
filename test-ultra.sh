#!/bin/bash

echo "🧪 Testing Ultra Dockerfile..."

# Build the ultra image
echo "📦 Building ultra image..."
docker build -f Dockerfile.ultra -t scanner-ultra . || {
    echo "❌ Build failed"
    exit 1
}

echo "✅ Build successful"

# Run the container
echo "🚀 Starting container..."
docker run -d -p 5000:5000 --name scanner-ultra-test scanner-ultra || {
    echo "❌ Failed to start container"
    exit 1
}

echo "⏳ Waiting for container to start..."
sleep 10

# Test the health endpoint
echo "🔍 Testing health endpoint..."
curl -f http://localhost:5000/health || {
    echo "❌ Health check failed"
    docker logs scanner-ultra-test
    docker stop scanner-ultra-test
    docker rm scanner-ultra-test
    exit 1
}

echo "✅ Health check passed"

# Test the main page
echo "🌐 Testing main page..."
curl -f http://localhost:5000/ > /dev/null || {
    echo "❌ Main page failed"
    docker logs scanner-ultra-test
    docker stop scanner-ultra-test
    docker rm scanner-ultra-test
    exit 1
}

echo "✅ Main page accessible"

# Test starting a scan
echo "🔍 Testing scan functionality..."
SCAN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"domain":"example.com"}' http://localhost:5000/scan)
echo "Scan response: $SCAN_RESPONSE"

if echo "$SCAN_RESPONSE" | grep -q '"success": true'; then
    echo "✅ Scan functionality working"
else
    echo "❌ Scan functionality failed"
    docker logs scanner-ultra-test
    docker stop scanner-ultra-test
    docker rm scanner-ultra-test
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up..."
docker stop scanner-ultra-test
docker rm scanner-ultra-test

echo "🎉 All tests passed! Ultra Dockerfile is working correctly."
echo "📍 You can now deploy this to Coolify using:"
echo "   - Dockerfile: Dockerfile.ultra"
echo "   - Docker Compose: docker-compose.ultra.yml"