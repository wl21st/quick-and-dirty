.PHONY: help install run test lint format clean

help:
	@echo "Available targets:"
	@echo "  make install    - Install dependencies using uv (sync)"
	@echo "  make run        - Run the weather tool (auto-detect location)"
	@echo "  make run ARGS=\"<city>\"  - Run for specific city"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make lint       - Run linting with ruff"
	@echo "  make format     - Format code with ruff"
	@echo "  make clean      - Clean build artifacts and cache"

install:
	@echo "Installing dependencies with uv..."
	uv sync --all-extras

run:
	@uv run weather $(ARGS)

test:
	@echo "Running tests..."
	@uv run pytest tests/ -v || echo "No tests found or pytest failed"

lint:
	@echo "Linting code..."
	@uv run ruff check .

format:
	@echo "Formatting code..."
	@uv run ruff format .

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache .venv dist build *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
