.PHONY: help dev test install clean format lint

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r backend/requirements.txt
	pip install -e .[dev]

dev:  ## Start development server
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	python -m pytest

test-cov:  ## Run tests with coverage
	python -m pytest --cov=backend/app --cov-report=html

format:  ## Format code with black
	black backend/ app.py

lint:  ## Lint code with ruff
	ruff check backend/

lint-fix:  ## Fix linting issues automatically
	ruff check --fix backend/

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

build:  ## Build the project
	python -m build

check: format lint test  ## Run all checks (format, lint, test) 