PIP_VERSION=24.0
UV_TOOLS_VERSION=0.2.23
SHELL=/bin/bash

# If we're running in CI then store Pytest output in a format which CircleCI can parse
ifdef CIRCLECI
MYPY_ARGS=--junit-xml=test-results/mypy.xml
endif

# Standard entry points
# =====================

.PHONY:dev
dev: install_python_packages .git/hooks/pre-commit

.PHONY:test
test:
	pytest

.PHONY:matrix_test
matrix_test:
	nox

.PHONY:lint
lint: ruff_format ruff_lint mypy

.PHONY:ruff_format
ruff_format:
	ruff format --check .

.PHONY:ruff_lint
ruff_lint:
	ruff check .

.PHONY:mypy
mypy:
	mypy $(MYPY_ARGS)

.PHONY:format
format:
	ruff format .
	ruff check --fix .

.PHONY:update
update:
	uv pip compile pyproject.toml -q --upgrade --resolver=backtracking --extra=dev --output-file=requirements/development.txt

.PHONY:package
package:
	pip wheel .

# Implementation details
# ======================

# Pip install all required Python packages
.PHONY:install_python_packages
install_python_packages: install_prerequisites requirements/development.txt
	uv pip sync requirements/development.txt requirements/firstparty.txt

# Install tools required to manage the project and its dependencies
.PHONY:install_prerequisites
install_prerequisites:
	@if [ `pip show pip | awk '/^Version:/ {print $$2}'` != "$(PIP_VERSION)" ]; then \
		pip install pip==$(PIP_VERSION); \
	fi
	@if [ `pip show uv | awk 'BEGIN{v=0} /^Version:/ {v=$$2} END{print v}'` != "$(UV_TOOLS_VERSION)" ]; then \
		pip install uv==$(UV_TOOLS_VERSION); \
	fi

# Add new dependencies to requirements/development.txt whenever pyproject.toml changes
requirements/development.txt: pyproject.toml
	uv pip compile pyproject.toml -q --extra=dev --output-file=requirements/development.txt

.git/hooks/pre-commit:
	@if type pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
	else \
		echo "WARNING: pre-commit not installed." > /dev/stderr; \
	fi
