# Video Foundry - Auto-fix Code Issues (Windows)
# Run this before committing to automatically fix formatting and linting issues

Write-Host "🔧 Auto-fixing Code Issues" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🐍 Fixing Python code..." -ForegroundColor Yellow
try {
    $null = Get-Command ruff -ErrorAction Stop

    Write-Host "   Running ruff auto-fix..." -ForegroundColor Gray
    ruff check backend/ workers/ tests/ --fix

    Write-Host "   Formatting code..." -ForegroundColor Gray
    ruff format backend/ workers/ tests/

    Write-Host "   ✅ Python code fixed and formatted" -ForegroundColor Green
} catch {
    Write-Host "   ❌ ruff not installed" -ForegroundColor Red
    Write-Host "      Install: pip install ruff" -ForegroundColor Gray
    exit 1
}

Write-Host ""

Write-Host "🎨 Fixing frontend code..." -ForegroundColor Yellow
if (Test-Path "frontend") {
    Set-Location frontend

    if (Test-Path "package.json") {
        try {
            $null = npm run lint:fix 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Frontend linting fixed" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  No lint:fix script in package.json" -ForegroundColor DarkYellow
            }
        } catch {
            Write-Host "   ⚠️  Could not run lint:fix" -ForegroundColor DarkYellow
        }

        try {
            $null = npm run format 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Frontend formatted" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  No format script in package.json" -ForegroundColor DarkYellow
            }
        } catch {
            Write-Host "   ⚠️  Could not run format" -ForegroundColor DarkYellow
        }
    }

    Set-Location ..
}

Write-Host ""

Write-Host "📝 Fixing line endings and whitespace..." -ForegroundColor Yellow
# PowerShell doesn't have sed, but we can skip this for now
# Most editors handle this automatically on Windows
Write-Host "   ⚠️  Manual whitespace cleanup recommended" -ForegroundColor DarkYellow
Write-Host "   (Most editors handle this automatically)" -ForegroundColor Gray

Write-Host ""
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "✅ Auto-fix complete!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Review changes: git diff" -ForegroundColor White
Write-Host "   2. Run tests: .\dev.ps1 test" -ForegroundColor White
Write-Host "   3. Commit: git commit -m 'your message'" -ForegroundColor White
