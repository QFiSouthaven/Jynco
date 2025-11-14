#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automatic troubleshooter for common Video Foundry issues
.DESCRIPTION
    Detects and fixes common problems:
    - Port conflicts
    - Docker daemon issues
    - Container startup failures
    - Missing environment configuration
#>

param(
    [switch]$AutoFix,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║         VIDEO FOUNDRY - AUTOMATIC TROUBLESHOOTER              ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ============================================================================
# ISSUE 1: Port 8000 Blocked (Windows Common Issue)
# ============================================================================

Write-Host "`n[1/5] Checking for port conflicts..." -ForegroundColor Yellow

function Test-PortBlocked {
    param([int]$Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $false  # Not blocked
    } catch {
        return $true   # Blocked
    }
}

$port8000Blocked = Test-PortBlocked 8000

if ($port8000Blocked) {
    Write-Host "✗ Port 8000 is BLOCKED (common on Windows)" -ForegroundColor Red
    Write-Host "  This is usually caused by Windows Hyper-V or Windows NAT" -ForegroundColor Gray

    if ($AutoFix -or (Read-Host "  Fix automatically? (Y/n)") -ne 'n') {
        Write-Host "  → Updating .env to use port 8001..." -ForegroundColor Cyan

        if (Test-Path ".env") {
            $content = Get-Content ".env" -Raw
            $content = $content -replace "BACKEND_PORT=8000", "BACKEND_PORT=8001"
            $content | Out-File ".env" -Encoding UTF8 -Force
            Write-Host "  ✓ Fixed! Backend will use port 8001" -ForegroundColor Green
        } else {
            Write-Host "  ✗ .env file not found. Run .\setup.ps1 first" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✓ Port 8000 is available" -ForegroundColor Green
}

# ============================================================================
# ISSUE 2: Docker Desktop Not Running
# ============================================================================

Write-Host "`n[2/5] Checking Docker Desktop..." -ForegroundColor Yellow

try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is NOT running" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and run this script again" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# ISSUE 3: Containers Stuck or Not Starting
# ============================================================================

Write-Host "`n[3/5] Checking container status..." -ForegroundColor Yellow

try {
    $containers = docker-compose ps --format json 2>&1 | ConvertFrom-Json

    if ($null -eq $containers -or $containers.Count -eq 0) {
        Write-Host "✗ No containers are running" -ForegroundColor Red

        if ($AutoFix -or (Read-Host "  Start containers now? (Y/n)") -ne 'n') {
            Write-Host "  → Starting all services..." -ForegroundColor Cyan
            docker-compose up -d
            Write-Host "  ✓ Services started" -ForegroundColor Green
        }
    } else {
        $healthyCount = 0
        foreach ($container in $containers) {
            if ($container.State -eq "running") {
                $healthyCount++
            } else {
                Write-Host "  ✗ $($container.Service) is $($container.State)" -ForegroundColor Red
            }
        }

        if ($healthyCount -eq $containers.Count) {
            Write-Host "✓ All $healthyCount containers are running" -ForegroundColor Green
        } else {
            Write-Host "⚠ Only $healthyCount/$($containers.Count) containers are healthy" -ForegroundColor Yellow

            if ($AutoFix -or (Read-Host "  Restart all containers? (Y/n)") -ne 'n') {
                Write-Host "  → Restarting services..." -ForegroundColor Cyan
                docker-compose restart
                Write-Host "  ✓ Services restarted" -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "✗ Could not check container status" -ForegroundColor Red
}

# ============================================================================
# ISSUE 4: Missing .env File
# ============================================================================

Write-Host "`n[4/5] Checking configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "✗ .env file is missing" -ForegroundColor Red

    if ($AutoFix -or (Read-Host "  Create from template? (Y/n)") -ne 'n') {
        if (Test-Path ".env.developer.example") {
            Copy-Item ".env.developer.example" ".env"
            Write-Host "  ✓ Created .env from template" -ForegroundColor Green
            Write-Host "  ⚠ You may need to edit .env for your environment" -ForegroundColor Yellow
        } else {
            Write-Host "  ✗ Template file .env.developer.example not found" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

# ============================================================================
# ISSUE 5: Service Health Check
# ============================================================================

Write-Host "`n[5/5] Testing service connectivity..." -ForegroundColor Yellow

function Test-ServiceHealth {
    param([string]$Name, [string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✓ $Name is responding" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ✗ $Name is not responding at $Url" -ForegroundColor Red
        return $false
    }
}

# Get ports from .env if it exists
$backendPort = 8000
$frontendPort = 5173

if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^BACKEND_PORT=(\d+)") { $backendPort = $matches[1] }
        if ($_ -match "^FRONTEND_PORT=(\d+)") { $frontendPort = $matches[1] }
    }
}

$services = @{
    "Backend API" = "http://localhost:$backendPort/health"
    "Frontend UI" = "http://localhost:$frontendPort"
}

$allHealthy = $true
foreach ($service in $services.Keys) {
    if (-not (Test-ServiceHealth $service $services[$service])) {
        $allHealthy = $false
    }
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n" + "═" * 70 -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "`n✓ ALL SYSTEMS OPERATIONAL`n" -ForegroundColor Green
    Write-Host "Access Video Foundry at: http://localhost:$frontendPort`n" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠ SOME ISSUES DETECTED`n" -ForegroundColor Yellow
    Write-Host "Recommended actions:" -ForegroundColor White
    Write-Host "  1. Run:  .\setup.ps1  (full automated setup)" -ForegroundColor Cyan
    Write-Host "  2. Check logs:  .\dev.ps1 logs" -ForegroundColor Cyan
    Write-Host "  3. Restart:  .\dev.ps1 restart`n" -ForegroundColor Cyan
}

Write-Host "For more help, see: docs/TROUBLESHOOTING.md`n" -ForegroundColor Gray
