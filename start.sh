#!/bin/bash
# Video Foundry Launch Script for Linux/WSL/Mac
# This script starts all Docker services with GPU support

set -e  # Exit on error

echo "========================================"
echo "Video Foundry - Launch Script"
echo "========================================"
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Docker is not running. Please start Docker first."
    exit 1
fi

echo "[1/4] Checking for existing services..."
if docker compose ps 2>/dev/null | grep -q "Up"; then
    echo "Found running services. Stopping them..."
    docker compose --env-file .env.local down
fi

echo
echo "[2/4] Building Docker images..."
docker compose --env-file .env.local build

echo
echo "[3/4] Starting services with GPU support..."
docker compose --env-file .env.local up -d

echo
echo "[4/4] Waiting for services to be ready..."
sleep 10

echo
echo "========================================"
echo "Service Status:"
echo "========================================"
docker compose ps

echo
echo "========================================"
echo -e "${GREEN}Video Foundry is now running!${NC}"
echo "========================================"
echo
echo "Backend API:       http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Frontend UI:       http://localhost:5173"
echo "RabbitMQ Console:  http://localhost:15672 (guest/guest)"
echo
echo "To view logs: docker compose logs -f"
echo "To stop:      docker compose down"
echo

# Check GPU access
echo "Verifying GPU access..."
if docker exec jynco-ai_worker-1 nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null; then
    echo -e "${GREEN}[SUCCESS]${NC} GPU is accessible to AI workers"
else
    echo -e "${YELLOW}[WARNING]${NC} Could not verify GPU access. Check NVIDIA drivers."
fi

echo
