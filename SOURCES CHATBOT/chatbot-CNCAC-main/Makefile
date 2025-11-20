# ChatDocAI Development Makefile
# Quick commands for local development with Docker Compose

.PHONY: help dev-start dev-stop dev-restart dev-logs dev-shell dev-clean
.PHONY: rebuild rebuild-frontend rebuild-backend
.PHONY: frontend backend database
.PHONY: setup test lint format

# Default target
.DEFAULT_GOAL := help

# Configuration
COMPOSE_FILE := docker-compose.dev.yml
ENV_FILE := .env

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)ChatDocAI Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup: ## Initial setup - copy env files and start services
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		cp .env.example $(ENV_FILE); \
		echo "$(GREEN)Created $(ENV_FILE) from template$(NC)"; \
	fi
	@if [ ! -f front/.env.local ]; then \
		cp front/.env.local.example front/.env.local; \
		echo "$(GREEN)Created front/.env.local from template$(NC)"; \
	fi
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "$(GREEN)Created backend/.env from template$(NC)"; \
	fi
	@echo "$(YELLOW)Please review and update environment files if needed$(NC)"

dev-start: ## Start all development services
	@echo "$(BLUE)Starting development services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services started:$(NC)"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Supabase: http://localhost:54321"

dev-stop: ## Stop all development services
	@echo "$(BLUE)Stopping development services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)All services stopped$(NC)"

dev-restart: ## Restart all development services
	@echo "$(BLUE)Restarting development services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)All services restarted$(NC)"

dev-logs: ## Show logs for all services
	@docker-compose -f $(COMPOSE_FILE) logs -f

dev-status: ## Show status of all services
	@docker-compose -f $(COMPOSE_FILE) ps

rebuild: ## Rebuild all services
	@echo "$(BLUE)Rebuilding all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@docker-compose -f $(COMPOSE_FILE) build --no-cache
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)All services rebuilt and started$(NC)"

rebuild-frontend: ## Rebuild only the frontend service
	@echo "$(BLUE)Rebuilding frontend...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) stop frontend
	@docker-compose -f $(COMPOSE_FILE) build --no-cache frontend
	@docker-compose -f $(COMPOSE_FILE) up -d frontend
	@echo "$(GREEN)Frontend rebuilt and restarted$(NC)"

rebuild-backend: ## Rebuild only the backend service
	@echo "$(BLUE)Rebuilding backend...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) stop backend
	@docker-compose -f $(COMPOSE_FILE) build --no-cache backend
	@docker-compose -f $(COMPOSE_FILE) up -d backend
	@echo "$(GREEN)Backend rebuilt and restarted$(NC)"

# Service-specific commands
frontend: ## Open frontend shell
	@docker-compose -f $(COMPOSE_FILE) exec frontend /bin/sh

backend: ## Open backend shell
	@docker-compose -f $(COMPOSE_FILE) exec backend /bin/bash

database: ## Open database shell
	@docker-compose -f $(COMPOSE_FILE) exec supabase psql -U postgres -d postgres

# Log commands for specific services
logs-frontend: ## Show frontend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f frontend

logs-backend: ## Show backend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-db: ## Show database logs
	@docker-compose -f $(COMPOSE_FILE) logs -f supabase

# Development helpers
dev-clean: ## Clean up containers, images, and volumes
	@echo "$(YELLOW)This will remove all containers, images, and volumes. Continue? [y/N]$(NC)"
	@read answer && [ $${answer:-N} = y ] && \
		docker-compose -f $(COMPOSE_FILE) down -v --rmi all && \
		docker system prune -f && \
		echo "$(GREEN)Cleanup completed$(NC)" || \
		echo "$(YELLOW)Cleanup cancelled$(NC)"

dev-reset: ## Reset everything (clean + rebuild)
	@echo "$(YELLOW)This will reset everything. Continue? [y/N]$(NC)"
	@read answer && [ $${answer:-N} = y ] && \
		$(MAKE) dev-clean && \
		$(MAKE) rebuild && \
		echo "$(GREEN)Reset completed$(NC)" || \
		echo "$(YELLOW)Reset cancelled$(NC)"

# Production commands
prod-start: ## Start production services
	@echo "$(BLUE)Starting production services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)Production services started$(NC)"

prod-stop: ## Stop production services
	@docker-compose down

# Testing
test: test-backend test-frontend ## Run all tests
	@echo "$(GREEN)All tests completed$(NC)"

test-backend: ## Run backend tests with coverage
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd backend && pytest --cov=src --cov-report=term-missing --cov-report=html

test-frontend: ## Run frontend tests with coverage
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd front && npm run test:coverage

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@cd backend && pytest tests/ -m integration --verbose

# Code quality
lint: lint-backend lint-frontend ## Run linters for both backend and frontend
	@echo "$(GREEN)Linting completed$(NC)"

lint-backend: ## Run backend linter
	@echo "$(BLUE)Linting backend...$(NC)"
	@cd backend && ruff check src/ tests/

lint-frontend: ## Run frontend linter
	@echo "$(BLUE)Linting frontend...$(NC)"
	@cd front && npm run lint

format: format-backend format-frontend ## Format code for both backend and frontend
	@echo "$(GREEN)Formatting completed$(NC)"

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend...$(NC)"
	@cd backend && ruff format src/ tests/

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	@cd front && npx prettier --write "src/**/*.{ts,tsx,js,jsx}"

typecheck: ## Run type checking for both backend and frontend
	@echo "$(BLUE)Running type checks...$(NC)"
	@cd backend && mypy src/ --ignore-missing-imports
	@cd front && npm run typecheck
	@echo "$(GREEN)Type checking completed$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@cd backend && safety check -r requirements.txt
	@cd front && npm audit
	@echo "$(GREEN)Security checks completed$(NC)"

pre-commit: lint typecheck test ## Run all checks before committing
	@echo "$(GREEN)All pre-commit checks passed!$(NC)"

ci-local: ## Run CI pipeline locally
	@echo "$(BLUE)Running CI pipeline locally...$(NC)"
	@$(MAKE) lint
	@$(MAKE) typecheck
	@$(MAKE) test
	@$(MAKE) security-check
	@echo "$(GREEN)CI pipeline complete!$(NC)"

install-hooks: ## Install git hooks
	@echo "$(BLUE)Installing git hooks...$(NC)"
	@echo "#!/bin/sh\nmake pre-commit" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)Git hooks installed!$(NC)"

coverage-report: ## Generate and open coverage reports
	@echo "$(BLUE)Generating coverage reports...$(NC)"
	@cd backend && pytest --cov=src --cov-report=html && open htmlcov/index.html
	@cd front && npm run test:coverage && open coverage/lcov-report/index.html