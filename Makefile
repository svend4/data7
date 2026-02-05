.PHONY: help build up down restart logs ps test clean

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

## help: Display this help message
help:
	@echo "$(BLUE)Meta-Orchestrator Switchboard - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

## build: Build Docker images
build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

## up: Start all services
up:
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "Frontend: http://localhost:80"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/docs"

## down: Stop all services
down:
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

## restart: Restart all services
restart: down up

## logs: View logs from all services
logs:
	docker-compose logs -f

## logs-backend: View backend logs
logs-backend:
	docker-compose logs -f backend

## logs-frontend: View frontend logs
logs-frontend:
	docker-compose logs -f frontend

## logs-db: View database logs
logs-db:
	docker-compose logs -f db

## ps: List running containers
ps:
	docker-compose ps

## test: Run all tests
test: test-backend test-frontend

## test-backend: Run backend tests
test-backend:
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

## test-backend-unit: Run backend unit tests only
test-backend-unit:
	@echo "$(BLUE)Running backend unit tests...$(NC)"
	cd backend && pytest tests/unit/ -v --cov=app --cov-report=term-missing

## test-backend-integration: Run backend integration tests only
test-backend-integration:
	@echo "$(BLUE)Running backend integration tests...$(NC)"
	cd backend && pytest tests/integration/ -v

## test-frontend: Run frontend tests
test-frontend:
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test -- --coverage

## lint: Run all linters
lint: lint-backend lint-frontend

## lint-backend: Run backend linters
lint-backend:
	@echo "$(BLUE)Running backend linters...$(NC)"
	cd backend && black --check app/ tests/
	cd backend && isort --check-only app/ tests/
	cd backend && flake8 app/ tests/
	cd backend && mypy app/

## lint-frontend: Run frontend linters
lint-frontend:
	@echo "$(BLUE)Running frontend linters...$(NC)"
	cd frontend && npm run lint

## format: Format code
format: format-backend format-frontend

## format-backend: Format backend code
format-backend:
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && black app/ tests/
	cd backend && isort app/ tests/

## format-frontend: Format frontend code
format-frontend:
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format

## clean: Remove containers, volumes, and build artifacts
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

## shell-backend: Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/bash

## shell-db: Open PostgreSQL shell
shell-db:
	docker-compose exec db psql -U switchboard -d switchboard

## migrate: Run database migrations
migrate:
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker-compose exec backend alembic upgrade head

## security-scan: Run security vulnerability scans
security-scan:
	@echo "$(BLUE)Running security scans...$(NC)"
	cd backend && bandit -r app/
	cd backend && safety check

## docs: Generate API documentation
docs:
	@echo "$(BLUE)Opening API documentation...$(NC)"
	@echo "Visit: http://localhost:8000/api/docs"
	open http://localhost:8000/api/docs || xdg-open http://localhost:8000/api/docs

## dev: Start development environment
dev:
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose up

## prod-build: Build production images
prod-build:
	@echo "$(BLUE)Building production images...$(NC)"
	docker-compose -f docker-compose.yml build --no-cache

## health: Check health of all services
health:
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -f http://localhost:8000/health && echo "$(GREEN)✓ Backend healthy$(NC)" || echo "$(RED)✗ Backend unhealthy$(NC)"
	@curl -f http://localhost:80/health && echo "$(GREEN)✓ Frontend healthy$(NC)" || echo "$(RED)✗ Frontend unhealthy$(NC)"
