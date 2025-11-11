@echo off
REM Video Foundry Launch Script for Windows
REM This script starts all Docker services with GPU support

echo ========================================
echo Video Foundry - Launch Script
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [1/4] Checking for existing services...
docker compose ps >nul 2>&1
if %errorlevel% equ 0 (
    echo Found existing services. Stopping them...
    docker compose --env-file .env.local down
)

echo.
echo [2/4] Building Docker images...
docker compose --env-file .env.local build

if %errorlevel% neq 0 (
    echo [ERROR] Build failed. Please check the output above.
    pause
    exit /b 1
)

echo.
echo [3/4] Starting services with GPU support...
docker compose --env-file .env.local up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services. Please check the output above.
    pause
    exit /b 1
)

echo.
echo [4/4] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo Service Status:
echo ========================================
docker compose ps

echo.
echo ========================================
echo Video Foundry is now running!
echo ========================================
echo.
echo Backend API:       http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Frontend UI:       http://localhost:5173
echo RabbitMQ Console:  http://localhost:15672 (guest/guest)
echo.
echo To view logs: docker compose logs -f
echo To stop:      docker compose down
echo.

REM Check GPU access
echo Verifying GPU access...
docker exec jynco-ai_worker-1 nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] GPU is accessible to AI workers
) else (
    echo [WARNING] Could not verify GPU access. Check NVIDIA drivers.
)

echo.
pause
