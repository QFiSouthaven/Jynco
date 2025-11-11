#!/bin/bash

# Jynco Project Launch Script
# This script launches the entire Jynco Video Foundry platform

set -e

echo "🚀 Launching Jynco Video Foundry Platform..."
echo "============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys:${NC}"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - RUNWAY_API_KEY"
    echo "   - STABILITY_API_KEY"
    echo ""
    read -p "Press Enter to continue with default values, or Ctrl+C to exit and configure..."
fi

echo ""
echo -e "${BLUE}📋 Configuration Check${NC}"
echo "======================"

# Check if essential API keys are configured
if grep -q "your_access_key" .env || grep -q "your_runway_api_key" .env; then
    echo -e "${YELLOW}⚠️  Warning: Some API keys are still using default values${NC}"
    echo "   The application will start, but AI features will not work without valid keys."
    echo ""
fi

# Stop any existing containers
echo ""
echo -e "${BLUE}🛑 Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Pull latest images (optional, comment out if you want to skip)
echo ""
echo -e "${BLUE}📥 Pulling Docker images...${NC}"
docker-compose pull || echo -e "${YELLOW}⚠️  Could not pull images, will use existing/build local${NC}"

# Build and start services
echo ""
echo -e "${BLUE}🏗️  Building and starting services...${NC}"
docker-compose up -d --build

echo ""
echo -e "${BLUE}⏳ Waiting for services to initialize...${NC}"
sleep 10

# Check service health
echo ""
echo -e "${BLUE}🏥 Checking service health...${NC}"
echo "=========================="

services=("postgres" "redis" "rabbitmq" "backend" "ai_worker" "composition_worker" "frontend")

all_healthy=true
for service in "${services[@]}"; do
    if docker-compose ps | grep "$service" | grep -q "Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ All services are running!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be healthy. Check logs with:${NC}"
    echo "   docker-compose logs -f"
fi

# Display access information
echo ""
echo -e "${BLUE}🌐 Access Points${NC}"
echo "================"
echo -e "${GREEN}Frontend UI:${NC}        http://localhost:3000"
echo -e "${GREEN}Backend API:${NC}        http://localhost:8000"
echo -e "${GREEN}API Docs:${NC}           http://localhost:8000/docs"
echo -e "${GREEN}RabbitMQ UI:${NC}        http://localhost:15672 (guest/guest)"
echo ""

# Display useful commands
echo -e "${BLUE}📝 Useful Commands${NC}"
echo "=================="
echo "View logs:          docker-compose logs -f"
echo "View specific:      docker-compose logs -f backend"
echo "Stop services:      docker-compose down"
echo "Restart service:    docker-compose restart backend"
echo "View status:        docker-compose ps"
echo ""

# Optionally open browser
if command -v xdg-open &> /dev/null; then
    read -p "Open frontend in browser? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000
    fi
elif command -v open &> /dev/null; then
    read -p "Open frontend in browser? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi

echo ""
echo -e "${GREEN}🎉 Launch complete! Your Video Foundry platform is ready.${NC}"
echo ""
