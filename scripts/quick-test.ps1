# Video Foundry - Quick Test Runner (Windows)
# Runs fast tests to validate changes

param(
    [Parameter(Position=0)]
    [ValidateSet('unit', 'integration', 'all', 'watch')]
    [string]$TestType = 'unit'
)

Write-Host "🧪 Running Quick Tests" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

switch ($TestType) {
    'unit' {
        Write-Host "Running unit tests (fast)..." -ForegroundColor Yellow
        Set-Location tests
        pytest -v -m "not integration and not e2e" --tb=short
        Set-Location ..
    }

    'integration' {
        Write-Host "Running integration tests..." -ForegroundColor Yellow
        Write-Host "⚠️  Make sure services are running (.\dev.ps1 up)" -ForegroundColor DarkYellow
        Start-Sleep -Seconds 2
        Set-Location tests
        pytest -v -m integration --tb=short
        Set-Location ..
    }

    'all' {
        Write-Host "Running all tests..." -ForegroundColor Yellow
        Set-Location tests
        pytest -v --tb=short
        Set-Location ..
    }

    'watch' {
        Write-Host "Running tests in watch mode..." -ForegroundColor Yellow
        Write-Host "⚠️  Install pytest-watch: pip install pytest-watch" -ForegroundColor DarkYellow
        Set-Location tests
        pytest-watch -- -v --tb=short
        Set-Location ..
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Tests completed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    exit 1
}
