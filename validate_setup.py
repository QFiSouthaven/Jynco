#!/usr/bin/env python3
"""
Video Foundry - Setup Validation Script
"""
import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def check_file(filepath):
    """Check if a file exists."""
    if Path(filepath).is_file():
        print(f"{GREEN}✓{NC} {filepath} exists")
        return True
    else:
        print(f"{RED}✗{NC} {filepath} is missing")
        return False

def check_directory(dirpath):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"{GREEN}✓{NC} {dirpath}/ exists")
        return True
    else:
        print(f"{RED}✗{NC} {dirpath}/ is missing")
        return False

def main():
    print("=" * 50)
    print("Video Foundry - Setup Validation")
    print("=" * 50)
    print()

    all_checks_passed = True

    # Check project structure
    print("1. Checking Project Structure")
    print("-" * 30)

    directories = [
        "backend",
        "backend/models",
        "backend/api",
        "backend/services",
        "backend/config",
        "backend/schemas",
        "workers",
        "workers/ai_worker",
        "workers/ai_worker/adapters",
        "workers/composition_worker",
        "frontend",
        "frontend/src",
        "frontend/src/api",
        "frontend/src/components",
        "frontend/src/features",
        "tests",
        "tests/e2e"
    ]

    for directory in directories:
        if not check_directory(directory):
            all_checks_passed = False

    print()

    # Check critical files
    print("2. Checking Critical Files")
    print("-" * 30)

    files = [
        "docker-compose.yml",
        "README.md",
        "VIDEO_FOUNDRY_README.md",
        ".env.example",
        "backend/Dockerfile",
        "backend/requirements.txt",
        "backend/main.py",
        "backend/__init__.py",
        "workers/ai_worker/worker.py",
        "workers/ai_worker/requirements.txt",
        "workers/ai_worker/Dockerfile",
        "workers/composition_worker/worker.py",
        "workers/composition_worker/requirements.txt",
        "workers/composition_worker/Dockerfile",
        "frontend/package.json",
        "frontend/Dockerfile.dev",
        "tests/requirements.txt",
        "tests/conftest.py",
        "tests/e2e/test_timeline_workflow.py"
    ]

    for file in files:
        if not check_file(file):
            all_checks_passed = False

    print()

    # Check backend files
    print("3. Checking Backend Structure")
    print("-" * 30)

    backend_files = [
        "backend/models/__init__.py",
        "backend/models/base.py",
        "backend/models/project.py",
        "backend/models/segment.py",
        "backend/models/render_job.py",
        "backend/models/user.py",
        "backend/api/__init__.py",
        "backend/api/projects.py",
        "backend/api/segments.py",
        "backend/api/render.py",
        "backend/services/__init__.py",
        "backend/services/orchestrator.py",
        "backend/services/rabbitmq_client.py",
        "backend/services/redis_client.py",
        "backend/services/s3_client.py",
        "backend/schemas/__init__.py",
        "backend/schemas/project.py",
        "backend/schemas/segment.py",
        "backend/schemas/render_job.py"
    ]

    for file in backend_files:
        if not check_file(file):
            all_checks_passed = False

    print()

    # Check AI worker adapters
    print("4. Checking AI Worker Adapters")
    print("-" * 30)

    adapter_files = [
        "workers/ai_worker/adapters/__init__.py",
        "workers/ai_worker/adapters/base.py",
        "workers/ai_worker/adapters/factory.py",
        "workers/ai_worker/adapters/runway.py",
        "workers/ai_worker/adapters/stability.py",
        "workers/ai_worker/adapters/mock.py"
    ]

    for file in adapter_files:
        if not check_file(file):
            all_checks_passed = False

    print()

    # Check frontend structure
    print("5. Checking Frontend Structure")
    print("-" * 30)

    frontend_files = [
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
        "frontend/src/index.css",
        "frontend/vite.config.ts",
        "frontend/tsconfig.json",
        "frontend/tailwind.config.js",
        "frontend/src/api/client.ts",
        "frontend/src/api/projects.ts",
        "frontend/src/components/Header.tsx",
        "frontend/src/features/projects/ProjectList.tsx",
        "frontend/src/features/timeline/TimelineEditor.tsx",
        "frontend/src/features/timeline/SegmentCard.tsx",
        "frontend/src/features/dashboard/Dashboard.tsx",
        "frontend/src/store/useProjectStore.ts"
    ]

    for file in frontend_files:
        if not check_file(file):
            all_checks_passed = False

    print()

    # Check .env file
    print("6. Checking Environment Configuration")
    print("-" * 30)

    if Path(".env").is_file():
        print(f"{GREEN}✓{NC} .env file exists")
    else:
        print(f"{YELLOW}⚠{NC} .env file missing")
        print(f"  Run: cp .env.example .env")
        all_checks_passed = False

    print()

    # Summary
    print("=" * 50)
    if all_checks_passed:
        print(f"{GREEN}✓ All checks passed!{NC}")
        print()
        print("Next steps:")
        print("1. Ensure Docker is installed and running")
        print("2. Configure .env with your settings")
        print("3. Start services: docker-compose up --build")
        print("4. Access frontend: http://localhost:3000")
        print("5. Access API docs: http://localhost:8000/docs")
    else:
        print(f"{RED}✗ Some checks failed{NC}")
        print()
        print("Please ensure all required files are present.")

    print()
    print("For detailed testing guide, see: DOCKER_TESTING_GUIDE.md")
    print("=" * 50)

    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
