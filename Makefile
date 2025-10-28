.PHONY: setup run test lint format clean help

help:
	@echo "Available targets:"
	@echo "  setup   - Install dependencies and setup environment"
	@echo "  run     - Launch Streamlit application"
	@echo "  test    - Run test suite"
	@echo "  lint    - Run ruff linter"
	@echo "  format  - Format code with black"
	@echo "  clean   - Remove cache and build artifacts"

setup:
	@echo "Setting up environment..."
	@if command -v uv > /dev/null 2>&1; then \
		echo "Using uv..."; \
		uv pip install -e ".[dev]"; \
	else \
		echo "Using pip..."; \
		pip install -e ".[dev]"; \
	fi
	@pre-commit install || echo "Pre-commit hooks not installed (optional)"

run:
	@echo "Starting Streamlit application..."
	streamlit run streamlit_app.py

test:
	@echo "Running tests..."
	pytest tests/ -v

lint:
	@echo "Running linter..."
	ruff check src/ tests/ streamlit_app.py

format:
	@echo "Formatting code..."
	black src/ tests/ streamlit_app.py
	ruff check --fix src/ tests/ streamlit_app.py

clean:
	@echo "Cleaning cache and artifacts..."
	@if exist data rmdir /s /q data
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist src\perps_forecaster\__pycache__ rmdir /s /q src\perps_forecaster\__pycache__
	@echo "Clean complete"
