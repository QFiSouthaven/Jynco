# Video Foundry - Development Automation (Windows PowerShell)
# This is the Windows equivalent of the Makefile
#
# Usage: .\dev.ps1 <command>
# Example: .\dev.ps1 up
#          .\dev.ps1 test
#          .\dev.ps1 help

param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [string]$Arg1,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

# Colors
function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorOutput "Video Foundry - Development Automation" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Usage:" "Yellow"
    Write-ColorOutput "  .\dev.ps1 <command>" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Docker Services:" "Cyan"
    Write-ColorOutput "  up              Start all services" "Green"
    Write-ColorOutput "  down            Stop all services" "Green"
    Write-ColorOutput "  restart         Restart all services" "Green"
    Write-ColorOutput "  stop            Stop services without removing containers" "Green"
    Write-ColorOutput "  start           Start existing containers" "Green"
    Write-ColorOutput "  rebuild         Rebuild and restart all services" "Green"
    Write-ColorOutput "  status          Show status of all services" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Development:" "Cyan"
    Write-ColorOutput "  dev             Start services with logs visible" "Green"
    Write-ColorOutput "  dev-backend     Start only backend with dependencies" "Green"
    Write-ColorOutput "  dev-frontend    Start only frontend with backend" "Green"
    Write-ColorOutput "  dev-workers     Start workers with dependencies" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Logs & Monitoring:" "Cyan"
    Write-ColorOutput "  logs            View logs from all services" "Green"
    Write-ColorOutput "  logs-backend    View backend logs" "Green"
    Write-ColorOutput "  logs-workers    View worker logs" "Green"
    Write-ColorOutput "  logs-frontend   View frontend logs" "Green"
    Write-ColorOutput "  logs-comfyui    View ComfyUI logs" "Green"
    Write-ColorOutput "  health          Check health of all services" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Testing:" "Cyan"
    Write-ColorOutput "  test            Run all tests" "Green"
    Write-ColorOutput "  test-unit       Run unit tests only" "Green"
    Write-ColorOutput "  test-integration Run integration tests" "Green"
    Write-ColorOutput "  test-e2e        Run end-to-end tests" "Green"
    Write-ColorOutput "  test-cov        Run tests with coverage" "Green"
    Write-ColorOutput "  test-frontend   Run frontend tests" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Code Quality:" "Cyan"
    Write-ColorOutput "  lint            Run linters on all code" "Green"
    Write-ColorOutput "  lint-backend    Lint Python code" "Green"
    Write-ColorOutput "  lint-frontend   Lint frontend code" "Green"
    Write-ColorOutput "  format          Format all code" "Green"
    Write-ColorOutput "  format-backend  Format Python code" "Green"
    Write-ColorOutput "  format-frontend Format frontend code" "Green"
    Write-ColorOutput "  check           Run all quality checks (lint + test)" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Database:" "Cyan"
    Write-ColorOutput "  db-migrate      Run database migrations" "Green"
    Write-ColorOutput "  db-rollback     Rollback last migration" "Green"
    Write-ColorOutput "  db-reset        Reset database (DANGEROUS!)" "Green"
    Write-ColorOutput "  db-shell        Open PostgreSQL shell" "Green"
    Write-ColorOutput "  redis-cli       Open Redis CLI" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Setup & Installation:" "Cyan"
    Write-ColorOutput "  install         Install all dependencies" "Green"
    Write-ColorOutput "  install-backend Install Python dependencies" "Green"
    Write-ColorOutput "  install-frontend Install frontend dependencies" "Green"
    Write-ColorOutput "  setup           Complete initial setup" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Cleanup:" "Cyan"
    Write-ColorOutput "  clean           Clean up containers and volumes" "Green"
    Write-ColorOutput "  clean-images    Remove all project images" "Green"
    Write-ColorOutput "  clean-all       Nuclear option - remove everything" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Utilities:" "Cyan"
    Write-ColorOutput "  shell-backend   Open shell in backend container" "Green"
    Write-ColorOutput "  shell-worker    Open shell in worker container" "Green"
    Write-ColorOutput "  shell-frontend  Open shell in frontend container" "Green"
    Write-ColorOutput "  scale-workers N Scale AI workers (.\dev.ps1 scale-workers 4)" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Quick Actions:" "Cyan"
    Write-ColorOutput "  quick-test      Start services and run tests" "Green"
    Write-ColorOutput "  quick-start     Alias for setup" "Green"
    Write-ColorOutput ""
}

# Command implementations
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "h" { Show-Help }
    "-h" { Show-Help }
    "--help" { Show-Help }

    # Docker Services
    "up" {
        Write-ColorOutput "Starting all services..." "Green"
        docker-compose up -d
        Write-ColorOutput "Services started! Frontend: http://localhost:5173" "Green"
    }

    "down" {
        Write-ColorOutput "Stopping all services..." "Yellow"
        docker-compose down
    }

    "restart" {
        Write-ColorOutput "Restarting all services..." "Yellow"
        docker-compose restart
    }

    "stop" {
        Write-ColorOutput "Stopping services..." "Yellow"
        docker-compose stop
    }

    "start" {
        Write-ColorOutput "Starting existing containers..." "Green"
        docker-compose start
    }

    "rebuild" {
        Write-ColorOutput "Rebuilding all services..." "Yellow"
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
    }

    "status" {
        Write-ColorOutput "Service Status:" "Cyan"
        docker-compose ps
    }

    # Development
    "dev" {
        Write-ColorOutput "Starting development environment..." "Green"
        docker-compose up
    }

    "dev-backend" {
        Write-ColorOutput "Starting backend development..." "Green"
        docker-compose up postgres redis rabbitmq backend
    }

    "dev-frontend" {
        Write-ColorOutput "Starting frontend development..." "Green"
        docker-compose up backend frontend
    }

    "dev-workers" {
        Write-ColorOutput "Starting workers..." "Green"
        docker-compose up postgres redis rabbitmq ai_worker composition_worker
    }

    # Logs
    "logs" {
        docker-compose logs -f
    }

    "logs-backend" {
        docker-compose logs -f backend
    }

    "logs-workers" {
        docker-compose logs -f ai_worker composition_worker
    }

    "logs-frontend" {
        docker-compose logs -f frontend
    }

    "logs-comfyui" {
        docker-compose logs -f comfyui
    }

    # Health
    "health" {
        Write-ColorOutput "Health Checks:" "Cyan"

        try {
            $backendStatus = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2).StatusCode
            Write-ColorOutput "Backend: $backendStatus" "Green"
        } catch {
            Write-ColorOutput "Backend: DOWN" "Red"
        }

        try {
            $frontendStatus = (Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2).StatusCode
            Write-ColorOutput "Frontend: $frontendStatus" "Green"
        } catch {
            Write-ColorOutput "Frontend: DOWN" "Red"
        }

        try {
            $comfyuiStatus = (Invoke-WebRequest -Uri "http://localhost:8188" -UseBasicParsing -TimeoutSec 2).StatusCode
            Write-ColorOutput "ComfyUI: $comfyuiStatus" "Green"
        } catch {
            Write-ColorOutput "ComfyUI: DOWN" "Red"
        }

        try {
            $rabbitmqStatus = (Invoke-WebRequest -Uri "http://localhost:15672" -UseBasicParsing -TimeoutSec 2).StatusCode
            Write-ColorOutput "RabbitMQ: $rabbitmqStatus" "Green"
        } catch {
            Write-ColorOutput "RabbitMQ: DOWN" "Red"
        }
    }

    # Testing
    "test" {
        Write-ColorOutput "Running all tests..." "Cyan"
        Set-Location tests
        pip install -q -r requirements.txt
        pytest -v
        Set-Location ..
    }

    "test-unit" {
        Write-ColorOutput "Running unit tests..." "Cyan"
        Set-Location tests
        pytest -v -m "not integration and not e2e"
        Set-Location ..
    }

    "test-integration" {
        Write-ColorOutput "Running integration tests..." "Cyan"
        Set-Location tests
        pytest -v -m integration
        Set-Location ..
    }

    "test-e2e" {
        Write-ColorOutput "Running E2E tests..." "Cyan"
        Set-Location tests
        pytest -v tests/e2e/
        Set-Location ..
    }

    "test-cov" {
        Write-ColorOutput "Running tests with coverage..." "Cyan"
        Set-Location tests
        pytest --cov=../backend --cov-report=html --cov-report=term
        Set-Location ..
    }

    "test-frontend" {
        Write-ColorOutput "Running frontend tests..." "Cyan"
        Set-Location frontend
        npm test
        Set-Location ..
    }

    # Code Quality
    "lint" {
        Write-ColorOutput "Running linters..." "Cyan"
        & $PSScriptRoot\dev.ps1 lint-backend
        & $PSScriptRoot\dev.ps1 lint-frontend
    }

    "lint-backend" {
        Write-ColorOutput "Linting Python code..." "Yellow"
        try {
            ruff check backend/ workers/ tests/
        } catch {
            Write-ColorOutput "ruff not installed. Run: pip install ruff" "Red"
        }
    }

    "lint-frontend" {
        Write-ColorOutput "Linting frontend code..." "Yellow"
        Set-Location frontend
        npm run lint
        Set-Location ..
    }

    "format" {
        Write-ColorOutput "Formatting code..." "Cyan"
        & $PSScriptRoot\dev.ps1 format-backend
        & $PSScriptRoot\dev.ps1 format-frontend
    }

    "format-backend" {
        Write-ColorOutput "Formatting Python code..." "Yellow"
        try {
            ruff format backend/ workers/ tests/
        } catch {
            Write-ColorOutput "ruff not installed. Run: pip install ruff" "Red"
        }
    }

    "format-frontend" {
        Write-ColorOutput "Formatting frontend code..." "Yellow"
        Set-Location frontend
        try {
            npm run format
        } catch {
            Write-ColorOutput "Add format script to package.json" "DarkYellow"
        }
        Set-Location ..
    }

    "check" {
        & $PSScriptRoot\dev.ps1 lint
        & $PSScriptRoot\dev.ps1 test
    }

    # Database
    "db-migrate" {
        Write-ColorOutput "Running database migrations..." "Cyan"
        docker-compose exec backend alembic upgrade head
    }

    "db-rollback" {
        Write-ColorOutput "Rolling back last migration..." "Yellow"
        docker-compose exec backend alembic downgrade -1
    }

    "db-reset" {
        Write-ColorOutput "Resetting database..." "Red"
        docker-compose down -v
        docker-compose up -d postgres
        Start-Sleep -Seconds 5
        docker-compose up -d backend
        & $PSScriptRoot\dev.ps1 db-migrate
    }

    "db-shell" {
        docker-compose exec postgres psql -U postgres -d videofoundry
    }

    "redis-cli" {
        docker-compose exec redis redis-cli
    }

    # Installation
    "install" {
        Write-ColorOutput "Installing dependencies..." "Cyan"
        & $PSScriptRoot\dev.ps1 install-backend
        & $PSScriptRoot\dev.ps1 install-frontend
    }

    "install-backend" {
        Write-ColorOutput "Installing backend dependencies..." "Yellow"
        Set-Location backend
        pip install -r requirements.txt
        Set-Location ..
        Set-Location workers\ai_worker
        pip install -r requirements.txt
        Set-Location ..\..
        Set-Location workers\composition_worker
        pip install -r requirements.txt
        Set-Location ..\..
        Set-Location tests
        pip install -r requirements.txt
        Set-Location ..
    }

    "install-frontend" {
        Write-ColorOutput "Installing frontend dependencies..." "Yellow"
        Set-Location frontend
        npm install
        Set-Location ..
    }

    "setup" {
        Write-ColorOutput "Setting up Video Foundry..." "Green"
        if (-not (Test-Path ".env")) {
            if (Test-Path ".env.example") {
                Copy-Item .env.example .env
            }
        }
        & $PSScriptRoot\dev.ps1 install
        & $PSScriptRoot\dev.ps1 up
        Write-ColorOutput "Setup complete! Visit http://localhost:5173" "Green"
    }

    # Cleanup
    "clean" {
        Write-ColorOutput "Cleaning up..." "Red"
        docker-compose down -v
    }

    "clean-images" {
        Write-ColorOutput "Removing images..." "Red"
        docker-compose down --rmi all
    }

    "clean-all" {
        Write-ColorOutput "Removing all containers, volumes, and images..." "Red"
        docker-compose down -v --rmi all
        Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force
    }

    # Utilities
    "shell-backend" {
        docker-compose exec backend /bin/bash
    }

    "shell-worker" {
        docker-compose exec ai_worker /bin/bash
    }

    "shell-frontend" {
        docker-compose exec frontend /bin/sh
    }

    "scale-workers" {
        $N = if ($Arg1) { $Arg1 } else { 2 }
        Write-ColorOutput "Scaling AI workers to $N instances..." "Yellow"
        docker-compose up -d --scale ai_worker=$N
    }

    # Quick Actions
    "quick-test" {
        & $PSScriptRoot\dev.ps1 up
        & $PSScriptRoot\dev.ps1 test
    }

    "quick-start" {
        & $PSScriptRoot\dev.ps1 setup
    }

    default {
        Write-ColorOutput "Unknown command: $Command" "Red"
        Write-ColorOutput "Run '.\dev.ps1 help' for usage" "Yellow"
        exit 1
    }
}
