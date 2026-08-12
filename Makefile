AGENT_OS_HOST ?= localhost
AGENT_OS_PORT ?= 7777
HEALTH_URL := http://$(AGENT_OS_HOST):$(AGENT_OS_PORT)/status

.PHONY: dev-backend dev-frontend dev test lint health test-backend lint-backend

dev-backend:
	cd backend && uv run python agent_os.py

dev-frontend:
	@echo "Frontend not implemented yet. Run from frontend/ when available."

dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals."

test: test-backend

test-backend:
	cd backend && uv run --extra dev pytest -q

lint: lint-backend

lint-backend:
	cd backend && uv run --extra dev ruff check .

health:
	curl -sf $(HEALTH_URL)
