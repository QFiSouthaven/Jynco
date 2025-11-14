#!/bin/bash

# Start Frontend Script
cd "$(dirname "$0")/frontend"

echo "=================================="
echo "Starting Local AI Agent Frontend"
echo "=================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "ERROR: node_modules not found!"
    echo "Please run: npm install"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found in frontend directory!"
    exit 1
fi

echo "Starting React development server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm start
