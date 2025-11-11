#!/bin/bash
# Video Foundry Logs Viewer for Linux/WSL/Mac
# This script shows logs from all services

echo "========================================"
echo "Video Foundry - Logs Viewer"
echo "========================================"
echo
echo "Press Ctrl+C to exit"
echo

docker compose --env-file .env.local logs -f
