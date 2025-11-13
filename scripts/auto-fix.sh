#!/bin/bash
# Auto-fix common code issues
# Run this before committing to automatically fix formatting and linting issues

set -e

echo "🔧 Auto-fixing Code Issues"
echo "========================="
echo ""

echo "🐍 Fixing Python code..."
if command -v ruff >/dev/null 2>&1; then
    echo "   Running ruff auto-fix..."
    ruff check backend/ workers/ tests/ --fix

    echo "   Formatting code..."
    ruff format backend/ workers/ tests/

    echo "   ✅ Python code fixed and formatted"
else
    echo "   ❌ ruff not installed"
    echo "      Install: pip install ruff"
    exit 1
fi

echo ""

echo "🎨 Fixing frontend code..."
if [ -d "frontend" ]; then
    cd frontend

    if [ -f "package.json" ]; then
        if npm run lint:fix >/dev/null 2>&1; then
            echo "   ✅ Frontend linting fixed"
        else
            echo "   ⚠️  No lint:fix script in package.json"
        fi

        if npm run format >/dev/null 2>&1; then
            echo "   ✅ Frontend formatted"
        else
            echo "   ⚠️  No format script in package.json"
        fi
    fi

    cd ..
fi

echo ""

echo "📝 Fixing line endings and whitespace..."
# Remove trailing whitespace
find backend workers tests -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

echo "   ✅ Whitespace cleaned"

echo ""
echo "========================="
echo "✅ Auto-fix complete!"
echo ""
echo "💡 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Run tests: make test"
echo "   3. Commit: git commit -m 'your message'"
