@echo off
REM Video Foundry Status Script for Windows
REM This script shows the status of all services

echo ========================================
echo Video Foundry - Service Status
echo ========================================
echo.

docker compose --env-file .env.local ps

echo.
echo ========================================
echo Health Check
echo ========================================
echo.

REM Check backend
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend API is responding
) else (
    echo [X] Backend API is not responding
)

REM Check frontend
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is responding
) else (
    echo [X] Frontend is not responding
)

REM Check RabbitMQ
curl -s http://localhost:15672 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] RabbitMQ is responding
) else (
    echo [X] RabbitMQ is not responding
)

echo.
echo ========================================
echo GPU Status
echo ========================================
docker exec jynco-ai_worker-1 nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv 2>nul
if %errorlevel% neq 0 (
    echo [X] Could not access GPU
)

echo.
pause
