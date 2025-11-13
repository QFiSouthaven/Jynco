#!/bin/bash
# Run all code quality checks
# This simulates what pre-commit hooks will do

set -e

echo "🔍 Running Code Quality Checks"
echo "=============================="
echo ""

exit_code=0

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

echo "📝 Checking for large files..."
large_files=$(find . -type f -size +10M -not -path '*/\.*' -not -path '*/node_modules/*' 2>/dev/null)
if [ -n "$large_files" ]; then
    echo "   ⚠️  Large files found:"
    echo "$large_files" | sed 's/^/      /'
else
    echo "   ✅ No large files"
fi

echo ""

echo "🐍 Checking Python code..."
if command -v ruff >/dev/null 2>&1; then
    echo "   Running ruff linter..."
    if ruff check backend/ workers/ tests/ --quiet; then
        echo "   ✅ Ruff checks passed"
    else
        echo "   ❌ Ruff found issues (run: ruff check --fix)"
        exit_code=1
    fi

    echo "   Running ruff formatter check..."
    if ruff format --check backend/ workers/ tests/ --quiet; then
        echo "   ✅ Code is properly formatted"
    else
        echo "   ⚠️  Code needs formatting (run: ruff format)"
        exit_code=1
    fi
else
    echo "   ⚠️  ruff not installed (pip install ruff)"
fi

echo ""

echo "🔒 Checking for secrets..."
if command -v detect-secrets >/dev/null 2>&1; then
    if detect-secrets scan --baseline .secrets.baseline >/dev/null 2>&1; then
        echo "   ✅ No secrets detected"
    else
        echo "   ⚠️  Possible secrets found"
        exit_code=1
    fi
else
    echo "   ⚠️  detect-secrets not installed (pip install detect-secrets)"
fi

echo ""

echo "📦 Checking dependencies..."
if [ -f "backend/requirements.txt" ]; then
    if command -v safety >/dev/null 2>&1; then
        echo "   Running safety check..."
        if safety check -r backend/requirements.txt --json >/dev/null 2>&1; then
            echo "   ✅ No known vulnerabilities"
        else
            echo "   ⚠️  Vulnerabilities found in dependencies"
        fi
    else
        echo "   ⚠️  safety not installed (pip install safety)"
    fi
fi

echo ""
echo "=============================="

if [ $exit_code -eq 0 ]; then
    echo "✅ All checks passed!"
else
    echo "⚠️  Some checks failed. Please review above."
fi

exit $exit_code
