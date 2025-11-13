#!/bin/bash
# Quick development environment check
# Run this before starting work to ensure everything is ready

set -e

echo "🔍 Video Foundry Development Check"
echo "==================================="
echo ""

exit_code=0

# Check Docker
echo "🐳 Checking Docker..."
if docker info >/dev/null 2>&1; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running"
    exit_code=1
fi

# Check Docker Compose
if docker-compose version >/dev/null 2>&1; then
    echo "   ✅ Docker Compose is available"
else
    echo "   ❌ Docker Compose is not available"
    exit_code=1
fi

echo ""

# Check Python
echo "🐍 Checking Python..."
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 --version | cut -d' ' -f2)
    echo "   ✅ Python $python_version"
else
    echo "   ⚠️  Python not found in PATH (optional for local dev)"
fi

echo ""

# Check Node.js
echo "📦 Checking Node.js..."
if command -v node >/dev/null 2>&1; then
    node_version=$(node --version)
    echo "   ✅ Node.js $node_version"
else
    echo "   ⚠️  Node.js not found (optional for local dev)"
fi

echo ""

# Check required tools
echo "🛠️  Checking dev tools..."
for tool in git make curl; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✅ $tool"
    else
        echo "   ❌ $tool is not installed"
        exit_code=1
    fi
done

echo ""

# Check .env file
echo "⚙️  Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env file not found (will use defaults)"
    if [ -f ".env.example" ]; then
        echo "      Run: cp .env.example .env"
    fi
fi

echo ""

# Check disk space
echo "💾 Checking disk space..."
available_space=$(df -h . | awk 'NR==2 {print $4}')
echo "   Available: $available_space"

echo ""

# Show summary
if [ $exit_code -eq 0 ]; then
    echo "✨ All checks passed! You're ready to develop."
    echo ""
    echo "Quick start:"
    echo "  make up    - Start all services"
    echo "  make dev   - Start with logs"
    echo "  make help  - Show all commands"
else
    echo "⚠️  Some checks failed. Please resolve the issues above."
fi

exit $exit_code
