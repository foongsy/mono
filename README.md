# mono

Agent chat app — Spec Kit feature `001-agent-chat-app`.

## Backend (AgentOS + AG-UI)

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set AI_GATEWAY_API_KEY for chat runs
cd backend && uv sync --extra dev
```

### Environment

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_GATEWAY_API_KEY` | for chat | — | Vercel AI Gateway API key |
| `LLM_MODEL_ID` | no | `google/gemini-3.5-flash-lite` | Gateway model id |
| `AI_GATEWAY_BASE_URL` | no | `https://ai-gateway.vercel.sh/v1` | OpenAI-compatible base URL |
| `AGENT_OS_HOST` | no | `0.0.0.0` | Bind host |
| `AGENT_OS_PORT` | no | `7777` | Bind port |

CORS allows `http://localhost:5173` and `http://127.0.0.1:5173`.

### Commands

| Command | Purpose |
|---------|---------|
| `make dev-backend` | Start AgentOS with AG-UI interface |
| `make health` | `curl GET /status` — process listening check (no LLM credential validation) |
| `make test-backend` | Run backend pytest suite |
| `make lint-backend` | Run ruff on backend |

### Health check

`GET /status` reports whether the AG-UI interface is mounted and the process is listening. It does **not** validate `AI_GATEWAY_API_KEY` or call the LLM. Use `make health` while the backend is running.

## Specs

See [specs/001-agent-chat-app/](specs/001-agent-chat-app/) for plan, tasks, and quickstart.
