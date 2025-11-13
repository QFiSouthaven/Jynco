#!/bin/bash
# Video Foundry - Claude Code Session Start Hook
# This runs automatically when Claude Code starts a new session

set -e

echo "🚀 Video Foundry Development Environment"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "⚠️  Docker is not running. Start Docker to use the development environment."
    echo "   Run: make up"
    exit 0
fi

# Check service status
echo "📊 Service Status:"
echo "-------------------"

# Function to check if a port is open
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $service (port $port)"
        return 0
    else
        echo "❌ $service (port $port) - Not running"
        return 1
    fi
}

# Check all services
all_running=true
check_port 8000 "Backend API" || all_running=false
check_port 5173 "Frontend" || all_running=false
check_port 5432 "PostgreSQL" || all_running=false
check_port 6379 "Redis" || all_running=false
check_port 5672 "RabbitMQ" || all_running=false
check_port 8188 "ComfyUI" || all_running=false

echo ""

# Show quick actions
if [ "$all_running" = false ]; then
    echo "💡 Quick Start:"
    echo "   make up        - Start all services"
    echo "   make dev       - Start in dev mode (with logs)"
    echo "   make status    - Check detailed status"
else
    echo "✨ All services running!"
    echo ""
    echo "🔗 Quick Links:"
    echo "   Frontend:  http://localhost:5173"
    echo "   Backend:   http://localhost:8000/docs"
    echo "   ComfyUI:   http://localhost:8188"
    echo "   RabbitMQ:  http://localhost:15672"
fi

echo ""
echo "📚 Useful Commands:"
echo "   make help      - Show all available commands"
echo "   make test      - Run tests"
echo "   make logs      - View service logs"
echo "   make health    - Check service health"
echo ""

# Show git status
echo "🔀 Git Status:"
echo "-------------------"
git branch --show-current | sed 's/^/   Branch: /'
git status --short | head -5 | sed 's/^/   /'
if [ $(git status --short | wc -l) -gt 5 ]; then
    echo "   ... and $(( $(git status --short | wc -l) - 5 )) more files"
fi

echo ""
echo "========================================"
