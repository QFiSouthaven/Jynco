@echo off
REM Video Foundry Logs Viewer for Windows
REM This script shows logs from all services

echo ========================================
echo Video Foundry - Logs Viewer
echo ========================================
echo.
echo Press Ctrl+C to exit
echo.

docker compose --env-file .env.local logs -f
