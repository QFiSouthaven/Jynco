#!/usr/bin/env bash
# Video Foundry - Automated Setup Script (Linux/Mac)
# One-click solution - no manual configuration needed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Symbols
CHECK="${GREEN}✓${NC}"
CROSS="${RED}✗${NC}"
ARROW="${CYAN}→${NC}"
WARN="${YELLOW}⚠${NC}"

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        VIDEO FOUNDRY - AUTOMATED SETUP                        ║
║        One-Click Solution - No Manual Configuration           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# ============================================================================
# STEP 1: VALIDATE PREREQUISITES
# ============================================================================

echo -e "\n${MAGENTA}═══ Validating Prerequisites ═══${NC}\n"

# Check Docker
echo -e "${ARROW} Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${CROSS} Docker is not running"
    echo -e "${YELLOW}Please start Docker and run this script again.${NC}"
    exit 1
fi
echo -e "${CHECK} Docker is running"

# Check Docker Compose
echo -e "${ARROW} Checking Docker Compose..."
if ! docker-compose --version > /dev/null 2>&1; then
    echo -e "${CROSS} Docker Compose not found"
    exit 1
fi
echo -e "${CHECK} Docker Compose is available"

# ============================================================================
# STEP 2: DETECT AND FIX PORT CONFLICTS
# ============================================================================

echo -e "\n${MAGENTA}═══ Detecting Port Conflicts ═══${NC}\n"

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1  # Port in use
    else
        return 0  # Port available
    fi
}

find_available_port() {
    local start_port=$1
    local port=$start_port
    while ! check_port $port; do
        ((port++))
        if [ $port -gt $((start_port + 100)) ]; then
            echo "Cannot find available port near $start_port"
            exit 1
        fi
    done
    echo $port
}

# Check ports
declare -A PORTS=(
    [BACKEND_PORT]=8000
    [FRONTEND_PORT]=5173
    [COMFYUI_PORT]=8188
    [POSTGRES_PORT]=5432
    [REDIS_PORT]=6379
    [RABBITMQ_PORT]=5672
    [RABBITMQ_MANAGEMENT_PORT]=15672
    [PORTAINER_PORT]=9000
)

declare -A ENV_CONFIG

for key in "${!PORTS[@]}"; do
    desired_port=${PORTS[$key]}
    echo -e "${ARROW} Checking port $desired_port for $key..."

    if check_port $desired_port; then
        echo -e "${CHECK} Port $desired_port is available"
        ENV_CONFIG[$key]=$desired_port
    else
        new_port=$(find_available_port $((desired_port + 1)))
        echo -e "${WARN} Port $desired_port is in use, using $new_port instead"
        ENV_CONFIG[$key]=$new_port
    fi
done

# ============================================================================
# STEP 3: CREATE .ENV FILE
# ============================================================================

echo -e "\n${MAGENTA}═══ Creating Configuration ═══${NC}\n"

SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cat > .env << EOF
# ============================================================================
# Video Foundry Configuration - Auto-Generated
# Created: $(date '+%Y-%m-%d %H:%M:%S')
# ============================================================================

# Execution Mode
JYNCO_EXECUTION_MODE=developer

# Application Settings
APP_NAME=Video Foundry
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-${SECRET_KEY}

# Ports (Auto-configured to avoid conflicts)
BACKEND_PORT=${ENV_CONFIG[BACKEND_PORT]}
FRONTEND_PORT=${ENV_CONFIG[FRONTEND_PORT]}

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/videofoundry
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=videofoundry
POSTGRES_PORT=${ENV_CONFIG[POSTGRES_PORT]}

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PORT=${ENV_CONFIG[REDIS_PORT]}

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
RABBITMQ_PORT=${ENV_CONFIG[RABBITMQ_PORT]}
RABBITMQ_MANAGEMENT_PORT=${ENV_CONFIG[RABBITMQ_MANAGEMENT_PORT]}

# ComfyUI
COMFYUI_URL=http://comfyui:8188
COMFYUI_PORT=${ENV_CONFIG[COMFYUI_PORT]}

# Storage (Local mode - no AWS needed)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./videos
S3_BUCKET=videofoundry-dev
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# AI API Keys (Optional)
RUNWAY_API_KEY=
STABILITY_API_KEY=

# CORS
CORS_ORIGINS=http://localhost:${ENV_CONFIG[FRONTEND_PORT]},http://127.0.0.1:${ENV_CONFIG[FRONTEND_PORT]}

# Portainer
PORTAINER_PORT=${ENV_CONFIG[PORTAINER_PORT]}

# Worker Configuration
WORKER_CONCURRENCY=2
WORKER_PREFETCH_COUNT=1

# Logging
LOG_LEVEL=INFO
EOF

echo -e "${CHECK} Configuration file created: .env"

# ============================================================================
# STEP 4: CLEANUP
# ============================================================================

echo -e "\n${MAGENTA}═══ Cleaning Up Existing Containers ═══${NC}\n"
echo -e "${ARROW} Stopping any running containers..."
docker-compose down 2>&1 > /dev/null
echo -e "${CHECK} Cleanup complete"

# ============================================================================
# STEP 5: START SERVICES
# ============================================================================

echo -e "\n${MAGENTA}═══ Starting Services ═══${NC}\n"
echo -e "${ARROW} Starting all containers (this may take 1-2 minutes)..."
docker-compose up -d

echo -e "${CHECK} All containers started"

# ============================================================================
# STEP 6: WAIT FOR SERVICES
# ============================================================================

echo -e "\n${MAGENTA}═══ Waiting for Services to Initialize ═══${NC}\n"

wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30

    echo -e "${ARROW} Waiting for $name..."
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" $url | grep -q "200\|302"; then
            echo -e "${CHECK} $name is ready"
            return 0
        fi
        ((attempt++))
        sleep 2
        echo -n "."
    done

    echo -e "\n${WARN} $name did not respond in time (may still be starting)"
    return 1
}

echo ""
wait_for_service "Backend API" "http://localhost:${ENV_CONFIG[BACKEND_PORT]}/health"
wait_for_service "Frontend UI" "http://localhost:${ENV_CONFIG[FRONTEND_PORT]}"
wait_for_service "ComfyUI" "http://localhost:${ENV_CONFIG[COMFYUI_PORT]}"

# ============================================================================
# STEP 7: VALIDATE
# ============================================================================

echo -e "\n${MAGENTA}═══ Validation ═══${NC}\n"
echo -e "${ARROW} Checking container status..."

docker-compose ps | tail -n +2 | while read line; do
    if echo "$line" | grep -q "Up"; then
        service=$(echo "$line" | awk '{print $1}')
        echo -e "${CHECK} $service is running"
    fi
done

# ============================================================================
# SUCCESS
# ============================================================================

echo -e "\n${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    ✓ SETUP COMPLETE!                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Video Foundry is now running!${NC}\n"

echo -e "Access your services at:\n"
echo -e "  Frontend UI:      ${YELLOW}http://localhost:${ENV_CONFIG[FRONTEND_PORT]}${NC}"
echo -e "  Backend API:      ${YELLOW}http://localhost:${ENV_CONFIG[BACKEND_PORT]}/docs${NC}"
echo -e "  ComfyUI:          ${YELLOW}http://localhost:${ENV_CONFIG[COMFYUI_PORT]}${NC}"
echo -e "  RabbitMQ Admin:   ${YELLOW}http://localhost:${ENV_CONFIG[RABBITMQ_MANAGEMENT_PORT]}${NC}"
echo -e "  Portainer:        ${YELLOW}http://localhost:${ENV_CONFIG[PORTAINER_PORT]}${NC}"
echo -e ""

echo -e "Useful Commands:\n"
echo -e "  Stop all services:     ${CYAN}make down${NC}"
echo -e "  View logs:             ${CYAN}make logs${NC}"
echo -e "  Restart services:      ${CYAN}make restart${NC}"
echo -e "  Check status:          ${CYAN}make status${NC}"
echo -e ""

# Open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${ARROW} Opening frontend in your browser..."
    sleep 2
    open "http://localhost:${ENV_CONFIG[FRONTEND_PORT]}"
fi

echo -e "\n${GREEN}Setup completed successfully! Happy building! 🚀${NC}\n"
