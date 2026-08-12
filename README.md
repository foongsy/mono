# mono

Traditional Chinese agent chat app — Spec Kit feature [`001-agent-chat-app`](specs/001-agent-chat-app/).

Stack: **assistant-ui** (AG-UI client) ↔ **Agno AgentOS** (`POST /agui`, `GET /status`) with **Vercel AI Gateway** → `google/gemini-3.5-flash-lite`.

## Prerequisites

- Node.js 20+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
# Backend
cp backend/.env.example backend/.env
# Set AI_GATEWAY_API_KEY in backend/.env for chat runs

cd backend && uv sync --extra dev

# Frontend
cp frontend/.env.example frontend/.env.local
# VITE_AGUI_URL defaults to http://localhost:7777/agui

cd frontend && npm install
```

## Environment

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_GATEWAY_API_KEY` | for chat | — | Vercel AI Gateway API key |
| `LLM_MODEL_ID` | no | `google/gemini-3.5-flash-lite` | Gateway model id |
| `AI_GATEWAY_BASE_URL` | no | `https://ai-gateway.vercel.sh/v1` | OpenAI-compatible base URL |
| `AGENT_OS_HOST` | no | `0.0.0.0` | Bind host |
| `AGENT_OS_PORT` | no | `7777` | Bind port |

### Frontend (`frontend/.env.local`)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `VITE_AGUI_URL` | yes | `http://localhost:7777/agui` | Full AG-UI run endpoint (**canonical — no separate base URL**) |

CORS on the backend allows `http://localhost:5173` and `http://127.0.0.1:5173`.

## Commands

| Command | Purpose |
|---------|---------|
| `make dev-backend` | Start AgentOS with AG-UI interface |
| `make dev-frontend` | Start Vite dev server (port 5173) |
| `make dev` | Hint to run backend + frontend in separate terminals |
| `make health` | `curl GET /status` — process listening (no LLM check) |
| `make test` | Backend pytest + frontend vitest |
| `make lint` | Backend ruff + frontend eslint |

## Health check

`GET /status` reports whether the AG-UI interface is mounted and the process is listening. It does **not** validate `AI_GATEWAY_API_KEY` or call the LLM.

```bash
make dev-backend   # terminal 1
make health        # terminal 2 → {"status":"available"}
```

## Quickstart validation (T031)

Automated coverage:

- Scenario 1 (health): `make health` with backend up — **pass**
- Scenario 2–3 (streaming / multi-turn): manual in browser at `http://localhost:5173` with valid `AI_GATEWAY_API_KEY`
- Scenario 4 (empty send): composer send disabled + Enter blocked for whitespace — **pass** (unit/UI guard)
- Scenario 5 (env URL): change `VITE_AGUI_URL`, restart frontend — manual
- Scenarios 6–8: manual browser checks per [quickstart.md](specs/001-agent-chat-app/quickstart.md)

## Specs

- [Plan](specs/001-agent-chat-app/plan.md)
- [Tasks](specs/001-agent-chat-app/tasks.md)
- [Quickstart](specs/001-agent-chat-app/quickstart.md)
