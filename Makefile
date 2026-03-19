.PHONY: help setup lock format lint test check run-api run-dashboard run-kobe-shot-poc db-bootstrap load-kobe-shots prepare-kobe-backend sync-players sync-teams sync-all clean

UV ?= uv
PYTHON_VERSION := $(strip $(file <.python-version))

help:
	@$(UV) run python -c "print('Targets: setup, lock, format, lint, test, check, run-api, run-dashboard, run-kobe-shot-poc, db-bootstrap, load-kobe-shots, prepare-kobe-backend, sync-players, sync-teams, sync-all, clean')"

setup:
	$(UV) python install $(PYTHON_VERSION)
	$(UV) sync --all-groups

lock:
	$(UV) lock

format:
	$(UV) run ruff format src tests scripts

lint:
	$(UV) run ruff check src tests scripts
	$(UV) run mypy src

test:
	$(UV) run pytest

check:
	$(UV) run ruff check src tests scripts
	$(UV) run pytest

run-api:
	$(UV) run nba-charts-api

run-dashboard:
	$(UV) run nba-charts-dashboard

run-kobe-shot-poc:
	$(UV) run nba-charts-kobe-shot-poc

db-bootstrap:
	$(UV) run nba-charts-db bootstrap

load-kobe-shots:
	$(UV) run nba-charts-db load-kobe-shots

prepare-kobe-backend:
	$(UV) run nba-charts-db prepare-kobe-backend

sync-players:
	$(UV) run nba-charts-sync players

sync-teams:
	$(UV) run nba-charts-sync teams

sync-all:
	$(UV) run nba-charts-sync all

clean:
	$(UV) run python scripts/clean.py
