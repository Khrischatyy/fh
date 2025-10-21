.PHONY: help dev prod test clean migrate upgrade downgrade shell format lint install

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:
	@echo "$(GREEN)Funny How FastAPI Backend - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make dev              - Build and run all services with Nginx (port 80)"
	@echo "  make dev-detach       - Run development server in background"
	@echo "  make dev-build        - Force rebuild and start development services"
	@echo "  make logs             - View API logs (follow mode)"
	@echo "  make logs-all         - View all service logs"
	@echo "  make restart          - Restart API container"
	@echo ""
	@echo "$(YELLOW)Production:$(NC)"
	@echo "  make prod             - Run production server"
	@echo "  make prod-detach      - Run production in background"
	@echo "  make prod-build       - Force rebuild and start production"
	@echo ""
	@echo "$(YELLOW)Database Migrations:$(NC)"
	@echo "  make migrate          - Apply all pending migrations"
	@echo "  make migrate-create   - Create new migration (requires message='description')"
	@echo "  make migrate-down     - Rollback last migration"
	@echo "  make migrate-history  - Show migration history"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  make test             - Run all tests with coverage"
	@echo "  make test-verbose     - Run tests with verbose output"
	@echo "  make test-watch       - Run tests in watch mode"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  make format           - Format code with black and ruff"
	@echo "  make lint             - Run linting checks"
	@echo "  make type-check       - Run mypy type checking"
	@echo ""
	@echo "$(YELLOW)Database:$(NC)"
	@echo "  make db-shell         - Open PostgreSQL shell"
	@echo "  make db-reset         - Reset database (WARNING: destructive)"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make shell            - Open Python shell in container"
	@echo "  make clean            - Stop and remove all containers and volumes"
	@echo "  make stop             - Stop all containers"
	@echo "  make ps               - Show running containers"
	@echo "  make install          - Install dependencies locally with uv"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make dev-build     - Build and start all services"
	@echo "  2. make migrate       - Run database migrations"
	@echo "  3. Visit http://localhost or http://localhost/docs"

# ==============================================================================
# Development Commands
# ==============================================================================

dev:
	@echo "$(GREEN)Starting development services...$(NC)"
	docker-compose -f dev.yml up

dev-detach:
	@echo "$(GREEN)Starting development services in background...$(NC)"
	docker-compose -f dev.yml up -d
	@echo "$(GREEN)Services started! API available at: http://localhost$(NC)"
	@echo "$(GREEN)API Docs: http://localhost/docs$(NC)"
	@echo "$(GREEN)RabbitMQ Management: http://localhost:15672$(NC)"

dev-build:
	@echo "$(GREEN)Building and starting development services...$(NC)"
	docker-compose -f dev.yml up --build

logs:
	docker-compose -f dev.yml logs -f api

logs-all:
	docker-compose -f dev.yml logs -f

logs-nginx:
	docker-compose -f dev.yml logs -f nginx

restart:
	@echo "$(GREEN)Restarting API container...$(NC)"
	docker-compose -f dev.yml restart api

# ==============================================================================
# Production Commands
# ==============================================================================

prod:
	@echo "$(GREEN)Starting production services...$(NC)"
	docker-compose -f prod.yml up

prod-detach:
	@echo "$(GREEN)Starting production services in background...$(NC)"
	docker-compose -f prod.yml up -d
	@echo "$(GREEN)Production services started! API available at: http://localhost$(NC)"

prod-build:
	@echo "$(GREEN)Building and starting production services...$(NC)"
	docker-compose -f prod.yml up --build -d

# ==============================================================================
# Database Migration Commands
# ==============================================================================

migrate:
	@echo "$(GREEN)Applying database migrations...$(NC)"
	docker-compose -f dev.yml exec api alembic upgrade head
	@echo "$(GREEN)Migrations applied successfully!$(NC)"

migrate-create:
	@if [ -z "$(message)" ]; then \
		echo "$(YELLOW)Usage: make migrate-create message='your migration description'$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating new migration: $(message)$(NC)"
	docker-compose -f dev.yml exec api alembic revision --autogenerate -m "$(message)"

migrate-down:
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	docker-compose -f dev.yml exec api alembic downgrade -1
	@echo "$(GREEN)Rollback complete$(NC)"

migrate-history:
	@echo "$(GREEN)Migration history:$(NC)"
	docker-compose -f dev.yml exec api alembic history

migrate-current:
	@echo "$(GREEN)Current migration:$(NC)"
	docker-compose -f dev.yml exec api alembic current

# Local migrations (without Docker)
migrate-local:
	@echo "$(GREEN)Applying migrations locally...$(NC)"
	alembic upgrade head

migrate-create-local:
	@if [ -z "$(message)" ]; then \
		echo "$(YELLOW)Usage: make migrate-create-local message='your migration description'$(NC)"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(message)"

migrate-down-local:
	alembic downgrade -1

# ==============================================================================
# Testing Commands
# ==============================================================================

test:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	docker-compose -f dev.yml exec api pytest tests/ -v --cov=src --cov-report=term-missing

test-verbose:
	docker-compose -f dev.yml exec api pytest tests/ -vv

test-watch:
	docker-compose -f dev.yml exec api pytest tests/ -v --cov=src -f

test-local:
	@echo "$(GREEN)Running tests locally...$(NC)"
	pytest tests/ -v --cov=src --cov-report=term-missing

test-cov-html:
	@echo "$(GREEN)Generating HTML coverage report...$(NC)"
	docker-compose -f dev.yml exec api pytest tests/ --cov=src --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

# ==============================================================================
# Code Quality Commands
# ==============================================================================

format:
	@echo "$(GREEN)Formatting code with black...$(NC)"
	black src/ tests/
	@echo "$(GREEN)Fixing issues with ruff...$(NC)"
	ruff check --fix src/ tests/

lint:
	@echo "$(GREEN)Checking code style with black...$(NC)"
	black --check src/ tests/
	@echo "$(GREEN)Linting with ruff...$(NC)"
	ruff check src/ tests/

type-check:
	@echo "$(GREEN)Running type checks with mypy...$(NC)"
	mypy src/

format-docker:
	docker-compose -f dev.yml exec api black src/ tests/
	docker-compose -f dev.yml exec api ruff check --fix src/ tests/

lint-docker:
	docker-compose -f dev.yml exec api black --check src/ tests/
	docker-compose -f dev.yml exec api ruff check src/ tests/

# ==============================================================================
# Database Commands
# ==============================================================================

db-shell:
	@echo "$(GREEN)Opening PostgreSQL shell...$(NC)"
	docker-compose -f dev.yml exec db psql -U postgres -d book_studio

db-reset:
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo "$(YELLOW)Resetting database...$(NC)"
	docker-compose -f dev.yml exec api alembic downgrade base
	docker-compose -f dev.yml exec api alembic upgrade head
	@echo "$(GREEN)Database reset complete$(NC)"

# ==============================================================================
# Utility Commands
# ==============================================================================

shell:
	@echo "$(GREEN)Opening Python shell in API container...$(NC)"
	docker-compose -f dev.yml exec api python

shell-bash:
	@echo "$(GREEN)Opening bash shell in API container...$(NC)"
	docker-compose -f dev.yml exec api /bin/sh

clean:
	@echo "$(YELLOW)Stopping and removing all containers, networks, and volumes...$(NC)"
	docker-compose -f dev.yml down -v
	docker-compose -f prod.yml down -v
	@echo "$(GREEN)Cleanup complete$(NC)"

stop:
	@echo "$(YELLOW)Stopping all containers...$(NC)"
	docker-compose -f dev.yml down
	docker-compose -f prod.yml down
	@echo "$(GREEN)All containers stopped$(NC)"

ps:
	@echo "$(GREEN)Running containers:$(NC)"
	docker-compose -f dev.yml ps

install:
	@echo "$(GREEN)Installing dependencies locally with uv...$(NC)"
	@if ! command -v uv &> /dev/null; then \
		echo "$(YELLOW)Installing uv...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	uv pip install -e ".[dev]"
	@echo "$(GREEN)Dependencies installed$(NC)"

install-prod:
	@echo "$(GREEN)Installing production dependencies with uv...$(NC)"
	uv pip install -e ".[prod]"

# ==============================================================================
# Docker Compose shortcuts
# ==============================================================================

build:
	docker-compose -f dev.yml build

build-prod:
	docker-compose -f prod.yml build

up: dev-detach

down: stop

# ==============================================================================
# Health Checks
# ==============================================================================

health:
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost/health || echo "$(YELLOW)API not responding$(NC)"

status:
	@echo "$(GREEN)Service Status:$(NC)"
	@docker-compose -f dev.yml ps

# ==============================================================================
# Quick setup for new developers
# ==============================================================================

setup: dev-build migrate
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Setup Complete!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "Your API is now running at:"
	@echo "  - API: $(GREEN)http://localhost$(NC)"
	@echo "  - Docs: $(GREEN)http://localhost/docs$(NC)"
	@echo "  - RabbitMQ: $(GREEN)http://localhost:15672$(NC) (guest/guest)"
	@echo ""
	@echo "To view logs: $(YELLOW)make logs$(NC)"
	@echo "To stop services: $(YELLOW)make stop$(NC)"
	@echo ""
