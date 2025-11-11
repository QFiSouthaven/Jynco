@echo off
REM Video Foundry Stop Script for Windows
REM This script stops all Docker services

echo ========================================
echo Video Foundry - Stop Script
echo ========================================
echo.

echo Stopping all services...
docker compose --env-file .env.local down

if %errorlevel% neq 0 (
    echo [ERROR] Failed to stop services.
    pause
    exit /b 1
)

echo.
echo ========================================
echo All services stopped successfully
echo ========================================
echo.
pause
