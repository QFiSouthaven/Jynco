#!/bin/bash
# Video Foundry Stop Script for Linux/WSL/Mac
# This script stops all Docker services

set -e

echo "========================================"
echo "Video Foundry - Stop Script"
echo "========================================"
echo

echo "Stopping all services..."
docker compose --env-file .env.local down

echo
echo "========================================"
echo "All services stopped successfully"
echo "========================================"
echo
