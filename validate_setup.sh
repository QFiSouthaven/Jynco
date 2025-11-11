#!/bin/bash
# Video Foundry - Setup Validation Script

set -e

echo "=================================="
echo "Video Foundry - Setup Validation"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/ exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ is missing"
        return 1
    fi
}

# Header
echo "1. Checking Prerequisites"
echo "-------------------------"
check_command docker || echo "   Install from: https://docs.docker.com/get-docker/"
check_command docker-compose || echo "   Usually included with Docker Desktop"
echo ""

# Check project structure
echo "2. Checking Project Structure"
echo "-----------------------------"
check_directory "backend"
check_directory "backend/models"
check_directory "backend/api"
check_directory "backend/services"
check_directory "workers"
check_directory "workers/ai_worker"
check_directory "workers/composition_worker"
check_directory "frontend"
check_directory "frontend/src"
check_directory "tests"
echo ""

# Check critical files
echo "3. Checking Critical Files"
echo "--------------------------"
check_file "docker-compose.yml"
check_file ".env" || echo "   Run: cp .env.example .env"
check_file "backend/Dockerfile"
check_file "backend/requirements.txt"
check_file "backend/main.py"
check_file "workers/ai_worker/worker.py"
check_file "workers/composition_worker/worker.py"
check_file "frontend/package.json"
echo ""

# Check Docker files
echo "4. Checking Dockerfiles"
echo "-----------------------"
check_file "backend/Dockerfile"
check_file "frontend/Dockerfile.dev"
check_file "workers/ai_worker/Dockerfile"
check_file "workers/composition_worker/Dockerfile"
echo ""

# Check requirements files
echo "5. Checking Dependencies"
echo "------------------------"
check_file "backend/requirements.txt"
check_file "workers/ai_worker/requirements.txt"
check_file "workers/composition_worker/requirements.txt"
check_file "frontend/package.json"
check_file "tests/requirements.txt"
echo ""

# Check ports
echo "6. Checking Port Availability"
echo "------------------------------"
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $1 is in use"
        lsof -Pi :$1 -sTCP:LISTEN | head -2
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

if command -v lsof &> /dev/null; then
    check_port 3000  # Frontend
    check_port 5432  # PostgreSQL
    check_port 5672  # RabbitMQ
    check_port 6379  # Redis
    check_port 8000  # Backend API
    check_port 15672 # RabbitMQ Management
else
    echo -e "${YELLOW}⚠${NC} lsof not available - skipping port check"
fi
echo ""

# Check .env configuration
echo "7. Checking .env Configuration"
echo "-------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    # Check for required variables
    grep -q "DATABASE_URL=" .env && echo -e "${GREEN}✓${NC} DATABASE_URL is set" || echo -e "${YELLOW}⚠${NC} DATABASE_URL not set"
    grep -q "REDIS_URL=" .env && echo -e "${GREEN}✓${NC} REDIS_URL is set" || echo -e "${YELLOW}⚠${NC} REDIS_URL not set"
    grep -q "RABBITMQ_URL=" .env && echo -e "${GREEN}✓${NC} RABBITMQ_URL is set" || echo -e "${YELLOW}⚠${NC} RABBITMQ_URL not set"
    grep -q "SECRET_KEY=" .env && echo -e "${GREEN}✓${NC} SECRET_KEY is set" || echo -e "${YELLOW}⚠${NC} SECRET_KEY not set"
else
    echo -e "${RED}✗${NC} .env file missing"
    echo "   Run: cp .env.example .env"
fi
echo ""

# Docker compose validation
echo "8. Validating docker-compose.yml"
echo "---------------------------------"
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} docker-compose.yml is valid"
    else
        echo -e "${RED}✗${NC} docker-compose.yml has errors"
        docker-compose config
    fi
else
    echo -e "${YELLOW}⚠${NC} docker-compose not available - skipping validation"
fi
echo ""

# Summary
echo "=================================="
echo "Validation Complete"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. If .env is missing: cp .env.example .env"
echo "2. Configure .env with your settings"
echo "3. Start services: docker-compose up --build"
echo "4. Access frontend: http://localhost:3000"
echo "5. Access API docs: http://localhost:8000/docs"
echo ""
echo "For detailed testing guide, see: DOCKER_TESTING_GUIDE.md"
