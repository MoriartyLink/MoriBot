#!/bin/bash

# Moriarty's Bot Docker Run Script
# Alternative method that works with sudo

echo "🐳 Moriarty's Bot Docker Runner"
echo "=================================="

# Stop existing container if running
if docker ps -q -f name=moribot 2>/dev/null; then
    echo "🛑 Stopping existing moribot container..."
    sudo docker stop moribot
    sudo docker rm moribot
fi

# Pull the latest image
echo "📥 Pulling latest moribot image..."
sudo docker pull ghcr.io/moriartylink/moribot:latest

# Create necessary directories if they don't exist
mkdir -p data logs

# Run the container with sudo
echo "🚀 Starting moribot container with sudo..."
sudo docker run -d \
    --name moribot \
    --restart unless-stopped \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/.env:/app/.env:ro \
    -v $(pwd)/session_*.session:/app/session_*.session \
    --network moribot-network \
    ghcr.io/moriartylink/moribot:latest

# Check if container started successfully
if docker ps -q -f name=moribot 2>/dev/null; then
    echo "✅ Moribot container started successfully!"
    echo ""
    echo "📊 Container Status:"
    sudo docker ps -f name=moribot
    echo ""
    echo "📱 Management Commands:"
    echo "   📱 View logs: sudo docker logs -f moribot"
    echo "   🛑 Stop: sudo docker stop moribot"
    echo "   🔄 Restart: sudo docker restart moribot"
    echo "   🗑️ Remove: sudo docker rm moribot"
else
    echo "❌ Failed to start moribot container"
    exit 1
fi
