#!/bin/bash

# Installation Verification Script
# Checks if the Local AI Agent is properly configured

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================="
echo "Local AI Agent - Installation Checker"
echo "======================================="
echo ""

ERRORS=0
WARNINGS=0

# Change to script directory
cd "$(dirname "$0")"

# Check 1: Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
    else
        echo -e "${RED}✗${NC} Python $PYTHON_VERSION (need 3.11+)"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} Python not found"
    ERRORS=$((ERRORS+1))
fi

# Check 2: Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
    ERRORS=$((ERRORS+1))
fi

# Check 3: Virtual environment
echo -n "Checking virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Not found (run: python3 -m venv venv)"
    ERRORS=$((ERRORS+1))
fi

# Check 4: Backend .env
echo -n "Checking backend .env file... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} Found"
    
    # Check for required variables
    if grep -q "GEMINI_API_KEY=" .env; then
        if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
            echo -e "  ${YELLOW}⚠${NC} GEMINI_API_KEY not configured"
            WARNINGS=$((WARNINGS+1))
        fi
    else
        echo -e "  ${RED}✗${NC} GEMINI_API_KEY missing"
        ERRORS=$((ERRORS+1))
    fi
    
    if ! grep -q "AGENT_SECRET_TOKEN=" .env; then
        echo -e "  ${RED}✗${NC} AGENT_SECRET_TOKEN missing"
        ERRORS=$((ERRORS+1))
    fi
    
    if ! grep -q "PROJECT_ROOT=" .env; then
        echo -e "  ${RED}✗${NC} PROJECT_ROOT missing"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} Not found (copy .env.example to .env)"
    ERRORS=$((ERRORS+1))
fi

# Check 5: Frontend directory
echo -n "Checking frontend... "
if [ -d "frontend" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Frontend directory not found"
    ERRORS=$((ERRORS+1))
fi

# Check 6: Frontend node_modules
echo -n "Checking frontend dependencies... "
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC} Not installed (run: cd frontend && npm install)"
    WARNINGS=$((WARNINGS+1))
fi

# Check 7: Frontend .env
echo -n "Checking frontend .env... "
if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓${NC} Found"
    
    if ! grep -q "REACT_APP_AGENT_API_KEY=" frontend/.env; then
        echo -e "  ${RED}✗${NC} REACT_APP_AGENT_API_KEY missing"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}✗${NC} Not found"
    ERRORS=$((ERRORS+1))
fi

# Check 8: Python dependencies
echo -n "Checking Python dependencies... "
if [ -f "venv/bin/python" ]; then
    if ./venv/bin/python -c "import fastapi, uvicorn, google.generativeai" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Installed"
    else
        echo -e "${YELLOW}⚠${NC} Some packages missing (run: pip install -r requirements.txt)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo -e "${YELLOW}⚠${NC} Cannot check (venv not set up)"
    WARNINGS=$((WARNINGS+1))
fi

# Check 9: Git
echo -n "Checking Git... "
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} $(git --version)"
else
    echo -e "${YELLOW}⚠${NC} Not found (optional)"
    WARNINGS=$((WARNINGS+1))
fi

# Check 10: Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✓${NC} Running"
    else
        echo -e "${YELLOW}⚠${NC} Installed but not running (optional)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo -e "${YELLOW}⚠${NC} Not found (optional)"
    WARNINGS=$((WARNINGS+1))
fi

# Summary
echo ""
echo "======================================="
echo "Summary"
echo "======================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Ready to start the system:"
    echo "  Terminal 1: ./start-backend.sh"
    echo "  Terminal 2: ./start-frontend.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
    echo "System should work but some optional features may be unavailable."
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before running the system."
    echo "See SETUP_GUIDE.md for detailed instructions."
    exit 1
fi
