# Video Foundry - Code Quality Check (Windows)
# This simulates what pre-commit hooks will do

Write-Host "🔍 Running Code Quality Checks" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

$exitCode = 0

# Check if we're in a git repo
try {
    $null = git rev-parse --git-dir 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Not in a git repository" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Not in a git repository" -ForegroundColor Red
    exit 1
}

Write-Host "📝 Checking for large files..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File | Where-Object {
    $_.Length -gt 10MB -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\node_modules\*"
}
if ($largeFiles) {
    Write-Host "   ⚠️  Large files found:" -ForegroundColor DarkYellow
    $largeFiles | ForEach-Object { Write-Host "      $($_.FullName)" -ForegroundColor Gray }
} else {
    Write-Host "   ✅ No large files" -ForegroundColor Green
}

Write-Host ""

Write-Host "🐍 Checking Python code..." -ForegroundColor Yellow
try {
    $null = Get-Command ruff -ErrorAction Stop

    Write-Host "   Running ruff linter..." -ForegroundColor Gray
    $null = ruff check backend/ workers/ tests/ --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Ruff checks passed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Ruff found issues (run: ruff check --fix)" -ForegroundColor Red
        $exitCode = 1
    }

    Write-Host "   Running ruff formatter check..." -ForegroundColor Gray
    $null = ruff format --check backend/ workers/ tests/ --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Code is properly formatted" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Code needs formatting (run: ruff format)" -ForegroundColor DarkYellow
        $exitCode = 1
    }
} catch {
    Write-Host "   ⚠️  ruff not installed (pip install ruff)" -ForegroundColor DarkYellow
}

Write-Host ""

Write-Host "🔒 Checking for secrets..." -ForegroundColor Yellow
try {
    $null = Get-Command detect-secrets -ErrorAction Stop
    $null = detect-secrets scan --baseline .secrets.baseline 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ No secrets detected" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Possible secrets found" -ForegroundColor DarkYellow
        $exitCode = 1
    }
} catch {
    Write-Host "   ⚠️  detect-secrets not installed (pip install detect-secrets)" -ForegroundColor DarkYellow
}

Write-Host ""

Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "backend\requirements.txt") {
    try {
        $null = Get-Command safety -ErrorAction Stop
        Write-Host "   Running safety check..." -ForegroundColor Gray
        $null = safety check -r backend\requirements.txt --json 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ No known vulnerabilities" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Vulnerabilities found in dependencies" -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "   ⚠️  safety not installed (pip install safety)" -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some checks failed. Please review above." -ForegroundColor DarkYellow
}

exit $exitCode
