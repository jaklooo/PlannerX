# PlannerX Makefile

.PHONY: help venv install dev test lint fmt migrate seed clean docker

# Default Python executable
PYTHON := python
PIP := $(PYTHON) -m pip

help:  ## Show this help message
	@echo "PlannerX - Task and Event Planner"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv:  ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Virtual environment created. Activate with: venv\Scripts\activate (Windows) or source venv/bin/activate (Unix)"

install:  ## Install dependencies
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed."

install-dev:  ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements-dev.txt
	@echo "Development dependencies installed."

dev:  ## Run development server
	@echo "Starting development server..."
	set FLASK_APP=wsgi.py && set FLASK_ENV=development && $(PYTHON) -m flask run --reload

prod:  ## Run production server with Gunicorn
	@echo "Starting production server..."
	gunicorn -c infra/gunicorn.conf.py wsgi:app

test:  ## Run tests
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:  ## Run linters
	@echo "Running linters..."
	$(PYTHON) -m ruff check app/ tests/ scripts/
	$(PYTHON) -m mypy app/ --ignore-missing-imports

fmt:  ## Format code
	@echo "Formatting code..."
	$(PYTHON) -m black app/ tests/ scripts/
	$(PYTHON) -m ruff check --fix app/ tests/ scripts/

migrate:  ## Run database migrations
	@echo "Running database migrations..."
	alembic upgrade head

migrate-create:  ## Create new migration
	@echo "Creating new migration..."
	@set /p MSG="Migration message: " && alembic revision --autogenerate -m "%MSG%"

seed:  ## Seed database with sample data
	@echo "Seeding database..."
	$(PYTHON) scripts/seed_dev.py

digest-run:  ## Run digest job manually
	@echo "Running daily digest job..."
	$(PYTHON) scripts/run_digest.py

test-email:  ## Send test email
	@set /p EMAIL="Recipient email: " && $(PYTHON) scripts/send_test_email.py %EMAIL%

clean:  ## Clean generated files
	@echo "Cleaning..."
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .coverage del .coverage
	if exist .ruff_cache rmdir /s /q .ruff_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	@echo "Cleaned."

docker-build:  ## Build Docker image
	@echo "Building Docker image..."
	docker build -f infra/docker/Dockerfile.api -t plannerx:latest .

docker-run:  ## Run Docker container
	@echo "Running Docker container..."
	docker run -d -p 5000:5000 --env-file .env plannerx:latest

docker-compose-up:  ## Start services with docker-compose
	@echo "Starting services..."
	docker-compose up -d

docker-compose-down:  ## Stop services
	@echo "Stopping services..."
	docker-compose down
