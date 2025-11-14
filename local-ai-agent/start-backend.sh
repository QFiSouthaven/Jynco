#!/bin/bash

# Start Backend Script
cd "$(dirname "$0")"

echo "=================================="
echo "Starting Local AI Agent Backend"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Start the server
echo "Starting FastAPI server on http://127.0.0.1:8000"
echo "API docs available at http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --host 127.0.0.1 --port 8000 --reload
