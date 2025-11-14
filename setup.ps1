#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated Video Foundry setup script - ONE CLICK SOLUTION
.DESCRIPTION
    Handles ALL setup tasks automatically:
    - Validates Docker is running
    - Checks for port conflicts and auto-fixes
    - Creates .env file with working configuration
    - Starts all services
    - Validates everything is running
    - Opens the UI in your browser
.NOTES
    Run this ONCE and you're done. No more manual configuration.
#>

param(
    [switch]$SkipBrowser,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "→ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Failure { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Section { param($msg) Write-Host "`n═══ $msg ═══`n" -ForegroundColor Magenta }

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        VIDEO FOUNDRY - AUTOMATED SETUP                        ║
║        One-Click Solution - No Manual Configuration           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ============================================================================
# STEP 1: VALIDATE PREREQUISITES
# ============================================================================

Write-Section "Validating Prerequisites"

# Check Docker Desktop
Write-Info "Checking Docker Desktop..."
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker is not running"
    }
    Write-Success "Docker Desktop is running"
} catch {
    Write-Failure "Docker Desktop is not running"
    Write-Host "`nPlease start Docker Desktop and run this script again.`n" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
Write-Info "Checking Docker Compose..."
try {
    docker-compose --version | Out-Null
    Write-Success "Docker Compose is available"
} catch {
    Write-Failure "Docker Compose not found"
    Write-Host "`nPlease install Docker Compose and try again.`n" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# STEP 2: DETECT AND FIX PORT CONFLICTS
# ============================================================================

Write-Section "Detecting Port Conflicts"

function Test-PortAvailable {
    param([int]$Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

function Find-AvailablePort {
    param([int]$StartPort)
    $port = $StartPort
    while (-not (Test-PortAvailable $port)) {
        $port++
        if ($port -gt $StartPort + 100) {
            throw "Cannot find available port near $StartPort"
        }
    }
    return $port
}

# Check required ports and auto-fix
$ports = @{
    "BACKEND_PORT" = 8000
    "FRONTEND_PORT" = 5173
    "COMFYUI_PORT" = 8188
    "POSTGRES_PORT" = 5432
    "REDIS_PORT" = 6379
    "RABBITMQ_PORT" = 5672
    "RABBITMQ_MANAGEMENT_PORT" = 15672
    "PORTAINER_PORT" = 9000
}

$envConfig = @{}

foreach ($key in $ports.Keys) {
    $desiredPort = $ports[$key]
    Write-Info "Checking port $desiredPort for $key..."

    if (Test-PortAvailable $desiredPort) {
        Write-Success "Port $desiredPort is available"
        $envConfig[$key] = $desiredPort
    } else {
        $newPort = Find-AvailablePort ($desiredPort + 1)
        Write-Warning "Port $desiredPort is in use, using $newPort instead"
        $envConfig[$key] = $newPort
    }
}

# ============================================================================
# STEP 3: CREATE .ENV FILE WITH WORKING CONFIGURATION
# ============================================================================

Write-Section "Creating Configuration"

$envContent = @"
# ============================================================================
# Video Foundry Configuration - Auto-Generated
# Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# ============================================================================

# Execution Mode
JYNCO_EXECUTION_MODE=developer

# Application Settings
APP_NAME=Video Foundry
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-$(New-Guid)

# Ports (Auto-configured to avoid conflicts)
BACKEND_PORT=$($envConfig['BACKEND_PORT'])
FRONTEND_PORT=$($envConfig['FRONTEND_PORT'])

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/videofoundry
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=videofoundry
POSTGRES_PORT=$($envConfig['POSTGRES_PORT'])

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PORT=$($envConfig['REDIS_PORT'])

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
RABBITMQ_PORT=$($envConfig['RABBITMQ_PORT'])
RABBITMQ_MANAGEMENT_PORT=$($envConfig['RABBITMQ_MANAGEMENT_PORT'])

# ComfyUI
COMFYUI_URL=http://comfyui:8188
COMFYUI_PORT=$($envConfig['COMFYUI_PORT'])

# Storage (Local mode - no AWS needed)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./videos
S3_BUCKET=videofoundry-dev
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# AI API Keys (Optional - leave empty to use local ComfyUI only)
RUNWAY_API_KEY=
STABILITY_API_KEY=

# CORS (Development)
CORS_ORIGINS=http://localhost:$($envConfig['FRONTEND_PORT']),http://127.0.0.1:$($envConfig['FRONTEND_PORT'])

# Portainer
PORTAINER_PORT=$($envConfig['PORTAINER_PORT'])

# Worker Configuration
WORKER_CONCURRENCY=2
WORKER_PREFETCH_COUNT=1

# Logging
LOG_LEVEL=INFO

# ============================================================================
# Quick Access URLs (after startup)
# ============================================================================
# Frontend:         http://localhost:$($envConfig['FRONTEND_PORT'])
# Backend API:      http://localhost:$($envConfig['BACKEND_PORT'])/docs
# ComfyUI:          http://localhost:$($envConfig['COMFYUI_PORT'])
# RabbitMQ Admin:   http://localhost:$($envConfig['RABBITMQ_MANAGEMENT_PORT'])
# Portainer:        http://localhost:$($envConfig['PORTAINER_PORT'])
# ============================================================================
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8 -Force
Write-Success "Configuration file created: .env"

# ============================================================================
# STEP 4: STOP ANY EXISTING CONTAINERS
# ============================================================================

Write-Section "Cleaning Up Existing Containers"

Write-Info "Stopping any running containers..."
docker-compose down 2>&1 | Out-Null
Write-Success "Cleanup complete"

# ============================================================================
# STEP 5: START ALL SERVICES
# ============================================================================

Write-Section "Starting Services"

Write-Info "Starting all containers (this may take 1-2 minutes)..."
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Failure "Failed to start services"
    Write-Host "`nRun 'docker-compose logs' to see error details.`n" -ForegroundColor Yellow
    exit 1
}

Write-Success "All containers started"

# ============================================================================
# STEP 6: WAIT FOR SERVICES TO BE HEALTHY
# ============================================================================

Write-Section "Waiting for Services to Initialize"

function Wait-ForService {
    param(
        [string]$Name,
        [string]$Url,
        [int]$MaxAttempts = 30
    )

    Write-Info "Waiting for $Name..."
    $attempts = 0

    while ($attempts -lt $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            Write-Success "$Name is ready"
            return $true
        } catch {
            $attempts++
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline
        }
    }

    Write-Warning "$Name did not respond in time (may still be starting)"
    return $false
}

Write-Host ""

# Wait for key services
$frontendUrl = "http://localhost:$($envConfig['FRONTEND_PORT'])"
$backendUrl = "http://localhost:$($envConfig['BACKEND_PORT'])/health"
$comfyuiUrl = "http://localhost:$($envConfig['COMFYUI_PORT'])"

Wait-ForService "Backend API" $backendUrl
Wait-ForService "Frontend UI" $frontendUrl
Wait-ForService "ComfyUI" $comfyuiUrl

# ============================================================================
# STEP 7: VALIDATE EVERYTHING IS WORKING
# ============================================================================

Write-Section "Validation"

Write-Info "Checking container status..."
$containers = docker-compose ps --format json | ConvertFrom-Json

$allHealthy = $true
foreach ($container in $containers) {
    $name = $container.Service
    $state = $container.State

    if ($state -eq "running") {
        Write-Success "$name is running"
    } else {
        Write-Warning "$name is $state"
        $allHealthy = $false
    }
}

# ============================================================================
# STEP 8: DISPLAY SUCCESS MESSAGE AND URLS
# ============================================================================

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    ✓ SETUP COMPLETE!                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Video Foundry is now running!`n" -ForegroundColor Cyan

Write-Host "Access your services at:" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend UI:      " -NoNewline; Write-Host "http://localhost:$($envConfig['FRONTEND_PORT'])" -ForegroundColor Yellow
Write-Host "  Backend API:      " -NoNewline; Write-Host "http://localhost:$($envConfig['BACKEND_PORT'])/docs" -ForegroundColor Yellow
Write-Host "  ComfyUI:          " -NoNewline; Write-Host "http://localhost:$($envConfig['COMFYUI_PORT'])" -ForegroundColor Yellow
Write-Host "  RabbitMQ Admin:   " -NoNewline; Write-Host "http://localhost:$($envConfig['RABBITMQ_MANAGEMENT_PORT'])" -ForegroundColor Yellow
Write-Host "  Portainer:        " -NoNewline; Write-Host "http://localhost:$($envConfig['PORTAINER_PORT'])" -ForegroundColor Yellow
Write-Host ""

Write-Host "Useful Commands:" -ForegroundColor White
Write-Host ""
Write-Host "  Stop all services:     " -NoNewline; Write-Host ".\dev.ps1 down" -ForegroundColor Cyan
Write-Host "  View logs:             " -NoNewline; Write-Host ".\dev.ps1 logs" -ForegroundColor Cyan
Write-Host "  Restart services:      " -NoNewline; Write-Host ".\dev.ps1 restart" -ForegroundColor Cyan
Write-Host "  Check status:          " -NoNewline; Write-Host ".\dev.ps1 status" -ForegroundColor Cyan
Write-Host ""

# Open browser automatically
if (-not $SkipBrowser) {
    Write-Info "Opening frontend in your browser..."
    Start-Sleep -Seconds 2
    Start-Process $frontendUrl
}

Write-Host "`nSetup completed successfully! Happy building! 🚀`n" -ForegroundColor Green

exit 0
