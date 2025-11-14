# Video Foundry - Environment Check (Windows)
# Run this before starting work to ensure everything is ready

Write-Host "🔍 Video Foundry Development Check" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$exitCode = 0

# Check Docker
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Docker is not running" -ForegroundColor Red
        $exitCode = 1
    }
} catch {
    Write-Host "   ❌ Docker is not running" -ForegroundColor Red
    $exitCode = 1
}

# Check Docker Compose
try {
    $null = docker-compose version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker Compose is available" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Docker Compose is not available" -ForegroundColor Red
        $exitCode = 1
    }
} catch {
    Write-Host "   ❌ Docker Compose is not available" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""

# Check Python
Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Python not found in PATH (optional for local dev)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "   ⚠️  Python not found in PATH (optional for local dev)" -ForegroundColor DarkYellow
}

Write-Host ""

# Check Node.js
Write-Host "📦 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Node.js $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Node.js not found (optional for local dev)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "   ⚠️  Node.js not found (optional for local dev)" -ForegroundColor DarkYellow
}

Write-Host ""

# Check required tools
Write-Host "🛠️  Checking dev tools..." -ForegroundColor Yellow
$tools = @("git")
foreach ($tool in $tools) {
    try {
        $null = & $tool --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $tool" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $tool is not installed" -ForegroundColor Red
            $exitCode = 1
        }
    } catch {
        Write-Host "   ❌ $tool is not installed" -ForegroundColor Red
        $exitCode = 1
    }
}

Write-Host ""

# Check .env file
Write-Host "⚙️  Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file not found (will use defaults)" -ForegroundColor DarkYellow
    if (Test-Path ".env.example") {
        Write-Host "      Run: Copy-Item .env.example .env" -ForegroundColor Gray
    }
}

Write-Host ""

# Check disk space
Write-Host "💾 Checking disk space..." -ForegroundColor Yellow
$drive = Get-PSDrive -Name C
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host "   Available: $freeGB GB" -ForegroundColor Green

Write-Host ""

# Show summary
if ($exitCode -eq 0) {
    Write-Host "✨ All checks passed! You're ready to develop." -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick start:" -ForegroundColor Cyan
    Write-Host "  .\dev.ps1 up       - Start all services" -ForegroundColor White
    Write-Host "  .\dev.ps1 dev      - Start with logs" -ForegroundColor White
    Write-Host "  .\dev.ps1 help     - Show all commands" -ForegroundColor White
} else {
    Write-Host "⚠️  Some checks failed. Please resolve the issues above." -ForegroundColor Red
}

exit $exitCode
