.PHONY: help dev prod test clean migrate

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help:
	@echo "$(GREEN)===========================================$(NC)"
	@echo "$(GREEN)Funny-How Platform - Available Commands$(NC)"
	@echo "$(GREEN)===========================================$(NC)"
	@echo ""
	@echo "$(BLUE)📦 Development:$(NC)"
	@echo "  make build            - Build all containers"
	@echo "  make dev              - Start all services (foreground)"
	@echo "  make dev-detach       - Start all services (background)"
	@echo "  make dev-build        - Build and start all services"
	@echo "  make stop             - Stop all services"
	@echo "  make restart          - Restart all services"
	@echo "  make status           - Show container status"
	@echo "  make logs             - View logs (use container=<name> for specific)"
	@echo "  make logs-all         - View all service logs"
	@echo ""
	@echo "$(BLUE)🚀 FastAPI Backend:$(NC)"
	@echo "  make migrate                 - Apply FastAPI migrations"
	@echo "  make migrate-create          - Create new migration (message='...')"
	@echo "  make migrate-down            - Rollback last migration"
	@echo "  make test                    - Run FastAPI tests"
	@echo "  make format                  - Format Python code"
	@echo "  make lint                    - Lint Python code"
	@echo "  make routes                  - List FastAPI routes"
	@echo "  make shell                   - Open Python shell"
	@echo ""
	@echo "$(BLUE)💾 Database:$(NC)"
	@echo "  make db-shell          - Open PostgreSQL shell"
	@echo "  make db-reset          - Reset database (WARNING: destructive)"
	@echo ""
	@echo "$(BLUE)🎨 Frontend:$(NC)"
	@echo "  make npm-install       - Install npm dependencies"
	@echo "  make update-frontend   - Restart frontend container"
	@echo ""
	@echo "$(BLUE)🧹 Cleanup:$(NC)"
	@echo "  make clean             - Stop and remove all containers"
	@echo "  make clean-all         - Remove ALL Docker resources (CAUTION)"
	@echo ""
	@echo "$(YELLOW)📍 Service URLs:$(NC)"
	@echo "  - FastAPI:          http://localhost (docs: /docs)"
	@echo "  - Frontend:         http://localhost:3000"
	@echo "  - Chat:             http://localhost:6001"
	@echo ""

# ==============================================================================
# Development Commands
# ==============================================================================

build:
	@echo "$(GREEN)Building all containers...$(NC)"
	@docker compose -f dev.yml build

dev:
	@echo "$(GREEN)Starting all services...$(NC)"
	@docker compose -f dev.yml up

dev-detach:
	@echo "$(GREEN)Starting all services in background...$(NC)"
	@docker compose -f dev.yml up -d
	@echo ""
	@echo "$(GREEN)✅ Services started!$(NC)"
	@echo "  - FastAPI:    $(BLUE)http://localhost$(NC) (docs: /docs)"
	@echo "  - Frontend:   $(BLUE)http://localhost:3000$(NC)"
	@echo "  - Chat:       $(BLUE)http://localhost:6001$(NC)"
	@echo ""

dev-build:
	@echo "$(GREEN)Building and starting all services...$(NC)"
	@docker compose -f dev.yml up --build

start: dev

stop:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker compose -f dev.yml down
	@echo "$(GREEN)All services stopped$(NC)"

restart: stop dev-detach

status:
	@echo "$(GREEN)Service Status:$(NC)"
	@docker compose -f dev.yml ps

logs:
	@docker compose -f dev.yml logs -f $(container)

logs-all:
	@docker compose -f dev.yml logs -f

logs-api:
	@docker compose -f dev.yml logs -f api

logs-celery:
	@docker compose -f dev.yml logs -f celery_worker

logs-frontend:
	@docker compose -f dev.yml logs -f frontend

logs-caddy:
	@docker compose -f dev.yml logs -f caddy

ps: status

# ==============================================================================
# FastAPI Backend Commands
# ==============================================================================

migrate:
	@echo "$(GREEN)Applying FastAPI migrations...$(NC)"
	@docker compose -f dev.yml exec api alembic upgrade head
	@echo "$(GREEN)✅ Migrations applied successfully!$(NC)"

migrate-create:
	@if [ -z "$(message)" ]; then \
		echo "$(YELLOW)Usage: make migrate-create message='your migration description'$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating new migration: $(message)$(NC)"
	@docker compose -f dev.yml exec api alembic revision --autogenerate -m "$(message)"

migrate-down:
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	@docker compose -f dev.yml exec api alembic downgrade -1
	@echo "$(GREEN)Rollback complete$(NC)"

migrate-history:
	@docker compose -f dev.yml exec api alembic history

test:
	@echo "$(GREEN)Running FastAPI tests...$(NC)"
	@docker compose -f dev.yml exec api pytest tests/ -v --cov=src --cov-report=term-missing

test-verbose:
	@docker compose -f dev.yml exec api pytest tests/ -vv

format:
	@echo "$(GREEN)Formatting Python code...$(NC)"
	@cd backend && black src/ tests/
	@cd backend && ruff check --fix src/ tests/

lint:
	@echo "$(GREEN)Linting Python code...$(NC)"
	@cd backend && black --check src/ tests/
	@cd backend && ruff check src/ tests/

shell:
	@echo "$(GREEN)Opening Python shell...$(NC)"
	@docker compose -f dev.yml exec api python

shell-bash:
	@docker compose -f dev.yml exec api /bin/sh

routes:
	@echo "$(GREEN)Listing all FastAPI routes...$(NC)"
	@docker compose -f dev.yml exec api python scripts/list_routes.py

# ==============================================================================
# Database Commands
# ==============================================================================

db-shell:
	@echo "$(GREEN)Opening PostgreSQL shell...$(NC)"
	@docker compose -f dev.yml exec db psql -U postgres -d book_studio

db-reset:
	@echo "$(YELLOW)⚠️  WARNING: This will delete all data!$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo "$(YELLOW)Resetting database...$(NC)"
	@docker compose -f dev.yml exec api alembic downgrade base
	@docker compose -f dev.yml exec api alembic upgrade head
	@echo "$(GREEN)Database reset complete$(NC)"

# ==============================================================================
# Frontend Commands
# ==============================================================================

npm-install:
	@echo "$(GREEN)Installing npm dependencies...$(NC)"
	@docker compose -f dev.yml run --rm frontend sh -c "npm i"

npm-install-package:
	@docker compose -f dev.yml run --rm frontend sh -c "npm i ${p}"

update-frontend:
	@echo "$(GREEN)Restarting frontend container...$(NC)"
	@docker compose -f dev.yml stop frontend
	@docker compose -f dev.yml up -d frontend

# ==============================================================================
# Celery Commands
# ==============================================================================

celery-status:
	@echo "$(GREEN)Checking Celery worker status...$(NC)"
	@docker compose -f dev.yml exec celery_worker celery -A src.tasks.celery_app inspect active

celery-stats:
	@echo "$(GREEN)Celery worker statistics...$(NC)"
	@docker compose -f dev.yml exec celery_worker celery -A src.tasks.celery_app inspect stats

celery-purge:
	@echo "$(YELLOW)Purging all Celery tasks...$(NC)"
	@docker compose -f dev.yml exec celery_worker celery -A src.tasks.celery_app purge -f

# ==============================================================================
# Production Commands
# ==============================================================================

prod:
	@echo "$(GREEN)Starting production services...$(NC)"
	@docker compose -f prod.yml up

prod-detach:
	@echo "$(GREEN)Starting production services in background...$(NC)"
	@docker compose -f prod.yml up -d

prod-build:
	@echo "$(GREEN)Building and starting production services...$(NC)"
	@docker compose -f prod.yml up --build -d

build-prod: prod-build

stop-prod:
	@docker compose -f prod.yml stop

status-prod:
	@docker compose -f prod.yml ps

logs-prod:
	@docker compose -f prod.yml logs -f $(container)

# ==============================================================================
# Cleanup Commands
# ==============================================================================

clean:
	@echo "$(YELLOW)Stopping and removing all containers...$(NC)"
	@docker compose -f dev.yml down -v
	@docker compose -f prod.yml down -v
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-prod:
	@docker compose -f prod.yml down --remove-orphans

clean-all:
	@echo "$(YELLOW)⚠️  WARNING: This will remove ALL Docker resources!$(NC)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@docker ps -a -q | xargs -r docker rm -f
	@docker volume ls -q | xargs -r docker volume rm
	@docker network ls --format '{{.Name}}' | awk '$$1 !~ /^(bridge|host|none)$$/' | xargs -r docker network rm
	@echo "$(GREEN)All Docker resources removed$(NC)"

# ==============================================================================
# Quick Setup
# ==============================================================================

setup: dev-build migrate
	@echo ""
	@echo "$(GREEN)=========================================$(NC)"
	@echo "$(GREEN)✅ Setup Complete!$(NC)"
	@echo "$(GREEN)=========================================$(NC)"
	@echo ""
	@echo "Your services are now running at:"
	@echo "  - FastAPI:    $(GREEN)http://localhost$(NC) (docs: /docs)"
	@echo "  - Frontend:   $(GREEN)http://localhost:3000$(NC)"
	@echo "  - Chat:       $(GREEN)http://localhost:6001$(NC)"
	@echo ""
	@echo "To view logs: $(YELLOW)make logs-all$(NC)"
	@echo "To stop services: $(YELLOW)make stop$(NC)"
	@echo ""

# ==============================================================================
# Health Checks
# ==============================================================================

health:
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost/health || echo "$(YELLOW)FastAPI not responding$(NC)"

# ==============================================================================
# Git
# ==============================================================================

pull:
	git pull

# ==============================================================================
# Utilities
# ==============================================================================

install:
	@echo "$(GREEN)Installing Python dependencies locally with uv...$(NC)"
	@if ! command -v uv &> /dev/null; then \
		echo "$(YELLOW)Installing uv...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	cd backend && uv pip install -e ".[dev]"
	@echo "$(GREEN)Dependencies installed$(NC)"
