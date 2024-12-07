.PHONY: help install test lint clean build docs coverage dev-install update-deps check check-all

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
FLAKE8 := $(VENV)/bin/flake8
BLACK := $(VENV)/bin/black
MYPY := $(VENV)/bin/mypy

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and set up virtual environment"
	@echo "  make test      - Run tests with pytest"
	@echo "  make lint      - Run linting checks (flake8, black, mypy)"
	@echo "  make clean     - Remove build artifacts and cache files"
	@echo "  make build     - Build distribution packages"
	@echo "  make docs      - Generate documentation"
	@echo "  make coverage  - Generate HTML coverage report"
	@echo "  make dev-install - Install development dependencies"
	@echo "  make update-deps - Update dependencies"
	@echo "  make check-all  - Run all checks (lint, test, coverage)"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

install: $(VENV)/bin/activate

test:
	$(PYTEST) tests/ -v --cov=openapi_cli_generator --cov-report=term-missing

lint:
	$(FLAKE8) openapi_cli_generator tests
	$(BLACK) --check openapi_cli_generator tests
	$(MYPY) openapi_cli_generator

format:
	$(BLACK) openapi_cli_generator tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf .eggs/
	rm -rf .hypothesis/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage.*" -delete
	find . -type f -name "coverage.xml" -delete

build: clean
	$(PYTHON) setup.py sdist bdist_wheel

docs:
	$(MAKE) -C docs html

check: lint test

coverage:
	$(PYTEST) tests/ -v --cov=openapi_cli_generator --cov-report=html
	@echo "HTML coverage report generated in htmlcov/"

dev-install:
	$(PIP) install -e ".[dev,test]"
	$(PIP) install pre-commit
	pre-commit install

update-deps:
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev,test]"

check-all: lint test coverage

.DEFAULT_GOAL := help
