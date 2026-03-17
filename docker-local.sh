#!/bin/bash

# Moriarty's Bot Local Docker Build
# Builds and runs the image locally without registry

echo "🏗 Moriarty's Bot Local Docker Build"
echo "======================================"

# Stop existing container if running
if docker ps -q -f name=moribot 2>/dev/null; then
    echo "🛑 Stopping existing moribot container..."
    sudo docker stop moribot
    sudo docker rm moribot
fi

# Build local image
echo "🔨 Building moribot image locally..."
sudo docker build -t moribot:latest .

# Create necessary directories if they don't exist
mkdir -p data logs

# Run the local image
echo "🚀 Starting moribot container from local image..."
sudo docker run -d \
    --name moribot \
    --restart unless-stopped \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/.env:/app/.env:ro \
    -v $(pwd)/session_*.session:/app/session_*.session \
    --network moribot-network \
    moribot:latest

# Check if container started successfully
if docker ps -q -f name=moribot 2>/dev/null; then
    echo "✅ Moribot container started successfully!"
    echo ""
    echo "📊 Container Status:"
    docker ps -f name=moribot
    echo ""
    echo "📱 Management Commands:"
    echo "   📱 View logs: docker logs -f moribot"
    echo "   🛑 Stop: docker stop moribot"
    echo "   🔄 Restart: docker restart moribot"
    echo "   🗑️ Remove: docker rm moribot"
    echo ""
    echo "💡 To rebuild: sudo docker build -t moribot:latest ."
else
    echo "❌ Failed to start moribot container"
    exit 1
fi
