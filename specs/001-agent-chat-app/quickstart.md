# Quickstart: Agent Chat App (001)

**Feature**: `specs/001-agent-chat-app`  
**Goal**: Validate end-to-end chat streaming, health check, and env-based backend URL without production deployment.

## Prerequisites

- Node.js 20+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed
- OpenAI API key with access to the configured model

## Environment

Create `backend/.env` (not committed):

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
AGENT_OS_HOST=0.0.0.0
AGENT_OS_PORT=7777
```

Create `frontend/.env.local` (not committed):

```bash
VITE_AGENTOS_URL=http://localhost:7777
```

## Commands (Constitution X)

From repository root after implementation lands:

| Command | Purpose |
|---------|---------|
| `make dev-backend` | Start Agno AgentOS |
| `make dev-frontend` | Start assistant-ui dev server |
| `make dev` | Start both |
| `make health` | Curl `GET /info` |
| `make test` | Run backend + frontend tests |
| `make lint` | Run linters |

CI MUST invoke the same `make test` and `make lint` targets.

## Scenario 1 — Health / status (User Story 3, SC-004)

1. Run `make dev-backend`
2. Run `make health` (or `curl -s http://localhost:7777/info`)
3. **Expect**: HTTP 200 JSON with `agent_count >= 1`
4. Stop backend; rerun health
5. **Expect**: connection failure (not ready)

**Pass**: Ready when listening; not ready when stopped — even if `OPENAI_API_KEY` is unset.

## Scenario 2 — Send message + streaming reply (User Story 1, SC-001, SC-002)

1. Set valid `OPENAI_API_KEY`
2. Run `make dev`
3. Open frontend URL (typically `http://localhost:5173`)
4. Enter Traditional Chinese: `請用三句話介紹你自己。`
5. Send
6. **Expect**:
   - User turn appears immediately
   - Assistant reply grows incrementally (multiple visible updates for a multi-sentence answer)
   - First characters within ~3s on local network (SC-001)
   - No page reload

## Scenario 3 — Multi-turn same thread (User Story 2, SC-003)

1. After Scenario 2 completes, send: `你剛才第一句話是什麼？`
2. **Expect**:
   - Both exchanges visible in one thread
   - Reply references recent context (within last N=10 turns)
   - Send disabled while streaming (FR-014)

## Scenario 4 — Empty message rejected (SC-006)

1. Submit whitespace-only input
2. **Expect**: No new user or assistant turn; no network call to `/runs`

## Scenario 5 — Backend URL via env (SC-005)

1. Change `VITE_AGENTOS_URL` to a different reachable AgentOS instance (or port)
2. Restart frontend dev server
3. **Expect**: Chat and health target new base URL without source edits

## Scenario 6 — Traditional Chinese replies (SC-007)

1. Send clear Traditional Chinese prompt: `今天天氣如何？請用繁體中文回答。`
2. **Expect**: Reply predominantly Traditional Chinese (not wholly another language)

## Scenario 7 — Stream failure handling

1. Stop backend mid-reply OR unset invalid API key and send
2. **Expect**: Error shown on assistant turn; user can send again after idle
3. **Expect**: No stop/cancel control in UI (clarification)

## Scenario 8 — No stop control (FR-014)

1. During streaming, verify UI has no cancel/stop button
2. Send button disabled until stream completes or fails

## References

- API contract: [contracts/api-v1.md](./contracts/api-v1.md)
- Data model: [data-model.md](./data-model.md)
- Research decisions: [research.md](./research.md)

## Next step

Run `/speckit-tasks` to generate implementation tasks from this plan.
