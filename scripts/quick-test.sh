#!/bin/bash
# Quick test runner for development
# Runs fast tests to validate changes

set -e

echo "🧪 Running Quick Tests"
echo "====================="
echo ""

# Default to unit tests, override with argument
TEST_TYPE=${1:-unit}

case $TEST_TYPE in
    unit)
        echo "Running unit tests (fast)..."
        cd tests
        pytest -v -m "not integration and not e2e" --tb=short
        ;;

    integration)
        echo "Running integration tests..."
        echo "⚠️  Make sure services are running (make up)"
        sleep 2
        cd tests
        pytest -v -m integration --tb=short
        ;;

    all)
        echo "Running all tests..."
        cd tests
        pytest -v --tb=short
        ;;

    watch)
        echo "Running tests in watch mode..."
        cd tests
        pytest-watch -- -v --tb=short
        ;;

    *)
        echo "Usage: $0 [unit|integration|all|watch]"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"
