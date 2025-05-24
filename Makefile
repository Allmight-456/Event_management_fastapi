.PHONY: help install setup migrate test lint format run clean

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

setup: install ## Set up development environment
	python scripts/setup_dev.py

migrate: ## Run database migrations
	alembic upgrade head

makemigration: ## Create a new migration (requires MESSAGE variable)
	alembic revision --autogenerate -m "$(MESSAGE)"

test: ## Run tests
	pytest -v --tb=short

test-coverage: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linting checks
	black . --check
	isort . --check-only
	flake8 .

format: ## Format code
	black .
	isort .

run: ## Start development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Start production server
	uvicorn app.main:app --host 0.0.0.0 --port 8000

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -f test_event_management.db
	rm -f test.db

docker-build: ## Build Docker image
	docker build -t event-management-api .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker Compose
	docker-compose down

init-db: ## Initialize database with sample data
	python scripts/create_migration.py
	make migrate
	python scripts/setup_dev.py

dev: ## Full development setup
	make install
	make init-db
	make run
