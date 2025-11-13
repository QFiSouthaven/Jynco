.PHONY: help up down restart status logs clean test lint format check install setup dev health

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Video Foundry - Development Automation$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Services

up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started! Frontend: http://localhost:5173$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker-compose restart

stop: ## Stop services without removing containers
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker-compose stop

start: ## Start existing containers
	@echo "$(GREEN)Starting existing containers...$(NC)"
	docker-compose start

rebuild: ## Rebuild and restart all services
	@echo "$(YELLOW)Rebuilding all services...$(NC)"
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

##@ Development

dev: ## Start services in development mode with live reload
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose up

dev-backend: ## Start only backend with dependencies
	@echo "$(GREEN)Starting backend development...$(NC)"
	docker-compose up postgres redis rabbitmq backend

dev-frontend: ## Start only frontend with backend
	@echo "$(GREEN)Starting frontend development...$(NC)"
	docker-compose up backend frontend

dev-workers: ## Start workers with dependencies
	@echo "$(GREEN)Starting workers...$(NC)"
	docker-compose up postgres redis rabbitmq ai_worker composition_worker

##@ Logs & Monitoring

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-workers: ## View worker logs
	docker-compose logs -f ai_worker composition_worker

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-comfyui: ## View ComfyUI logs
	docker-compose logs -f comfyui

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

health: ## Check health of all services
	@echo "$(BLUE)Health Checks:$(NC)"
	@echo "Backend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 'DOWN')"
	@echo "Frontend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173 || echo 'DOWN')"
	@echo "ComfyUI: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8188 || echo 'DOWN')"
	@echo "RabbitMQ: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:15672 || echo 'DOWN')"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	cd tests && pip install -q -r requirements.txt && pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd tests && pytest -v -m "not integration and not e2e"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd tests && pytest -v -m integration

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd tests && pytest -v tests/e2e/

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd tests && pytest --cov=../backend --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

##@ Code Quality

lint: ## Run linters on all code
	@echo "$(BLUE)Running linters...$(NC)"
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend

lint-backend: ## Lint Python code
	@echo "$(YELLOW)Linting Python code...$(NC)"
	@command -v ruff >/dev/null 2>&1 && ruff check backend/ workers/ tests/ || echo "$(RED)ruff not installed. Run: pip install ruff$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(YELLOW)Linting frontend code...$(NC)"
	cd frontend && npm run lint

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-backend
	@$(MAKE) format-frontend

format-backend: ## Format Python code
	@echo "$(YELLOW)Formatting Python code...$(NC)"
	@command -v ruff >/dev/null 2>&1 && ruff format backend/ workers/ tests/ || echo "$(RED)ruff not installed. Run: pip install ruff$(NC)"

format-frontend: ## Format frontend code
	@echo "$(YELLOW)Formatting frontend code...$(NC)"
	cd frontend && npm run format || echo "Add format script to package.json"

check: ## Run all quality checks (lint + test)
	@$(MAKE) lint
	@$(MAKE) test

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker-compose exec backend alembic upgrade head

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	docker-compose exec backend alembic downgrade -1

db-reset: ## Reset database (DANGEROUS!)
	@echo "$(RED)Resetting database...$(NC)"
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	docker-compose up -d backend
	@$(MAKE) db-migrate

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d videofoundry

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

##@ Setup & Installation

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(MAKE) install-backend
	@$(MAKE) install-frontend

install-backend: ## Install Python dependencies
	@echo "$(YELLOW)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	cd workers/ai_worker && pip install -r requirements.txt
	cd workers/composition_worker && pip install -r requirements.txt
	cd tests && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	@echo "$(YELLOW)Installing frontend dependencies...$(NC)"
	cd frontend && npm install

setup: ## Complete initial setup
	@echo "$(GREEN)Setting up Video Foundry...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || echo "No .env.example found"; fi
	@$(MAKE) install
	@$(MAKE) up
	@echo "$(GREEN)Setup complete! Visit http://localhost:5173$(NC)"

##@ Cleanup

clean: ## Clean up containers and volumes
	@echo "$(RED)Cleaning up...$(NC)"
	docker-compose down -v

clean-images: ## Remove all project images
	@echo "$(RED)Removing images...$(NC)"
	docker-compose down --rmi all

clean-all: ## Nuclear option - remove everything
	@echo "$(RED)Removing all containers, volumes, and images...$(NC)"
	docker-compose down -v --rmi all
	rm -rf backend/__pycache__ workers/**/__pycache__ tests/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

##@ Utilities

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-worker: ## Open shell in worker container
	docker-compose exec ai_worker /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

watch: ## Watch service status
	watch -n 2 'docker-compose ps'

scale-workers: ## Scale AI workers (usage: make scale-workers N=4)
	docker-compose up -d --scale ai_worker=$(or $(N),2)

##@ Git Operations

commit: ## Stage changes and commit (requires message: make commit M="your message")
	@if [ -z "$(M)" ]; then echo "$(RED)Error: Commit message required. Usage: make commit M=\"your message\"$(NC)"; exit 1; fi
	git add .
	git commit -m "$(M)"

push: ## Push to current branch
	git push -u origin $$(git branch --show-current)

pull: ## Pull from current branch
	git pull origin $$(git branch --show-current)

##@ Quick Actions

quick-test: up test ## Start services and run tests
quick-start: setup ## Alias for setup
dashboard: ## Open all dashboards in browser
	@echo "$(BLUE)Opening dashboards...$(NC)"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:5173 || open http://localhost:5173 || echo "Visit http://localhost:5173"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8000/docs || open http://localhost:8000/docs || echo "Visit http://localhost:8000/docs"
