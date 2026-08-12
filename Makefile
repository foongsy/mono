AGENT_OS_HOST ?= localhost
AGENT_OS_PORT ?= 7777
HEALTH_URL := http://$(AGENT_OS_HOST):$(AGENT_OS_PORT)/status

.PHONY: dev-backend dev-frontend dev test lint health test-backend test-frontend lint-backend lint-frontend

dev-backend:
	cd backend && uv run python agent_os.py

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals."

test: test-backend test-frontend

test-backend:
	cd backend && uv run --extra dev pytest -q

test-frontend:
	cd frontend && npm test

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run --extra dev ruff check .

lint-frontend:
	cd frontend && npm run lint

health:
	curl -sf $(HEALTH_URL)
