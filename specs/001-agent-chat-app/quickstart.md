# Quickstart: Agent Chat App (001)

**Feature**: `specs/001-agent-chat-app`  
**Protocol**: AG-UI (assistant-ui ↔ Agno `AGUI` interface)

## Prerequisites

- Node.js 20+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed
- OpenAI API key

## Environment

`backend/.env`:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
AGENT_OS_HOST=0.0.0.0
AGENT_OS_PORT=7777
```

`frontend/.env.local`:

```bash
VITE_AGUI_URL=http://localhost:7777/agui
```

## Commands

| Command | Purpose |
|---------|---------|
| `make dev-backend` | Start AgentOS with AGUI interface |
| `make dev-frontend` | Start assistant-ui dev server |
| `make dev` | Start both |
| `make health` | `curl GET /status` |
| `make test` | Backend + frontend tests |
| `make lint` | Linters |

## Scenario 1 — Health / status (SC-004)

1. `make dev-backend`
2. `make health` or `curl -sf http://localhost:7777/status`
3. **Expect**: HTTP 200
4. Stop backend → health fails
5. **Pass**: Ready without valid OpenAI key

## Scenario 2 — Streaming chat (SC-001, SC-002)

1. Valid `OPENAI_API_KEY`; `make dev`
2. Open frontend (`http://localhost:5173`)
3. Send: `請用三句話介紹你自己。`
4. **Expect**: Incremental assistant text via AG-UI stream
5. **SC-001 timing**: From send click, first assistant characters appear within **3 seconds** on local network (stopwatch or browser Performance marks acceptable for manual check)
6. **SC-002**: For a multi-sentence reply, at least two distinct UI updates before completion

## Scenario 3 — Multi-turn (SC-003)

1. Follow-up: `你剛才第一句話是什麼？`
2. **Expect**: Both exchanges in one thread; context within last 10 turns; send disabled while streaming

## Scenario 4 — Empty message (SC-006)

1. Whitespace-only send
2. **Expect**: No `/agui` request; no new turns

## Scenario 5 — Env URL (SC-005)

1. Change `VITE_AGUI_URL`; restart frontend
2. **Expect**: Chat targets new backend without code edits

## Scenario 6 — Traditional Chinese (SC-007)

1. `今天天氣如何？請用繁體中文回答。`
2. **Expect**: Predominantly Traditional Chinese reply
3. **Manual rubric**: Pass if ≥80% of visible reply characters are Traditional Chinese (or clearly TC prose); fail if the entire reply is another natural language (e.g. English-only or Simplified-only body)

## Scenario 7 — Errors

1. Invalid key or stopped backend during send
2. **Expect**: Error on turn (`RUN_ERROR`); can send again

## Scenario 8 — No stop control (FR-014)

1. No cancel/stop button during stream
2. Send disabled until run completes

## References

- [contracts/ag-ui-v1.md](./contracts/ag-ui-v1.md)
- [data-model.md](./data-model.md)
- [research.md](./research.md)
- [assistant-ui AG-UI quickstart](https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart)
- [Agno AG-UI interface](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction)

## Next step

`/speckit-tasks`
