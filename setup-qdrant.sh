#!/bin/bash

# Qdrant Local Server Setup Script
# This script will install Docker and start Qdrant on http://localhost:6333

set -e

echo "=================================="
echo "Qdrant Local Server Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on WSL
if ! grep -qi microsoft /proc/version; then
    echo -e "${YELLOW}Warning: This script is optimized for WSL2 on Windows${NC}"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Step 1: Checking Docker installation..."
if command_exists docker; then
    echo -e "${GREEN}✓ Docker is already installed${NC}"
    docker --version
else
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    echo "Please run the following commands manually (requires sudo):"
    echo ""
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y docker.io"
    echo "  sudo usermod -aG docker \$USER"
    echo "  sudo service docker start"
    echo ""
    echo "After installation, log out and log back in, then run this script again."
    exit 1
fi

echo ""
echo "Step 2: Checking if Docker service is running..."
if sudo service docker status >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker service is running${NC}"
else
    echo -e "${YELLOW}Starting Docker service...${NC}"
    sudo service docker start
    sleep 2
fi

echo ""
echo "Step 3: Checking if Qdrant container exists..."
if docker ps -a | grep -q qdrant; then
    echo -e "${YELLOW}Found existing Qdrant container${NC}"

    if docker ps | grep -q qdrant; then
        echo -e "${GREEN}✓ Qdrant is already running${NC}"
    else
        echo "Starting existing Qdrant container..."
        docker start qdrant
        sleep 2
    fi
else
    echo "Creating new Qdrant container..."

    # Create storage directory
    mkdir -p ./qdrant_storage

    # Run Qdrant
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant:latest

    echo "Waiting for Qdrant to start..."
    sleep 5
fi

echo ""
echo "Step 4: Verifying Qdrant is accessible..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:6333/ >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant is accessible at http://localhost:6333${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Waiting for Qdrant to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Failed to connect to Qdrant${NC}"
    echo "Check logs with: docker logs qdrant"
    exit 1
fi

echo ""
echo "Step 5: Getting Qdrant info..."
curl -s http://localhost:6333/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:6333/

echo ""
echo ""
echo "=================================="
echo -e "${GREEN}✓ Qdrant Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Qdrant is now running at:"
echo "  REST API: http://localhost:6333"
echo "  gRPC API: http://localhost:6334"
echo "  Web UI:   http://localhost:6333/dashboard"
echo ""
echo "Data is stored in: ./qdrant_storage/"
echo ""
echo "Useful commands:"
echo "  docker logs qdrant          - View logs"
echo "  docker stop qdrant          - Stop server"
echo "  docker start qdrant         - Start server"
echo "  docker restart qdrant       - Restart server"
echo "  docker rm -f qdrant         - Remove container"
echo ""
echo "Test the API:"
echo "  curl http://localhost:6333/"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:6333/dashboard in your browser"
echo "  2. Add Qdrant MCP server to .kilocode/mcp.json (see QDRANT-SETUP-GUIDE.md)"
echo "  3. Install Python client: pip install qdrant-client"
echo ""
