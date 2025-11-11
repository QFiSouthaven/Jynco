#!/bin/bash
# Video Foundry Status Script for Linux/WSL/Mac
# This script shows the status of all services

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "Video Foundry - Service Status"
echo "========================================"
echo

docker compose --env-file .env.local ps

echo
echo "========================================"
echo "Health Check"
echo "========================================"
echo

# Check backend
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Backend API is responding"
else
    echo -e "${RED}[X]${NC} Backend API is not responding"
fi

# Check frontend
if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Frontend is responding"
else
    echo -e "${RED}[X]${NC} Frontend is not responding"
fi

# Check RabbitMQ
if curl -s http://localhost:15672 >/dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} RabbitMQ is responding"
else
    echo -e "${RED}[X]${NC} RabbitMQ is not responding"
fi

echo
echo "========================================"
echo "GPU Status"
echo "========================================"
if docker exec jynco-ai_worker-1 nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} GPU is accessible"
else
    echo -e "${RED}[X]${NC} Could not access GPU"
fi

echo
