#!/bin/bash
#
# Jynco Parallel Agent Demo Runner
#
# This script runs the parallel initialization demo with proper setup
#

set -e

echo "🎬 Jynco - Video Generation Foundry"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p projects cache temp logs
echo "✓ Directories created"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo ""
    echo "📥 Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch venv/.installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Run the demo
echo ""
echo "🚀 Starting Parallel Agent Initialization Demo..."
echo "===================================="
echo ""

python3 examples/parallel_initialization_demo.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Demo completed successfully!"
    echo ""
    echo "📂 Check the following:"
    echo "  - projects/proj_demo_*/storyboard.json"
    echo "  - cache/"
    echo "  - logs/jynco.log (if logging to file)"
else
    echo "❌ Demo failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
