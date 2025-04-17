.PHONY: run test coverage clean install logs

# Variables
PYTHON = python
APP_PATH = app/main.py
VENV_NAME = venv
VENV_BIN = $(VENV_NAME)/bin
PYTEST = pytest

# Default target
all: install run

# Run the application
run:
	$(PYTHON) $(APP_PATH)

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	$(PYTEST)

# Run tests with coverage
coverage:
	$(PYTEST) --cov=app tests/

# View logs
logs:
	tail -f logs/app.log

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 