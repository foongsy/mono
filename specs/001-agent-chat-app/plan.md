# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`  
**User stack directive**: assistant-ui frontend, Agno SDK backend with AgentOS enabled

## Summary

Build a minimal Traditional Chinese agent chat web app: one browser thread, streaming replies from a real external LLM via Agno AgentOS, process-listening health check, and frontend backend URL configured by environment variable. Frontend uses **assistant-ui** (`useExternalStoreRuntime` + `Thread`). Backend runs a single **Agno AgentOS** instance exposing `GET /info` and `POST /agents/chat-agent/runs` (SSE). No login, database, RAG, tools, attachments, or production deployment in v1. Context window **N = 10** turns supplied by the frontend adapter.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)

**Primary Dependencies**:
- Backend: `agno`, `openai` (via Agno model), `uvicorn`
- Frontend: `@assistant-ui/react`, `@assistant-ui/react-markdown`, React 19, Vite 6

**Storage**: N/A — session-only in browser memory (FR-009); AgentOS without `db` in v1

**Testing**: pytest + httpx (backend integration); vitest (frontend unit for slice/guards)

**Target Platform**: Local dev — Linux/macOS; desktop browser

**Project Type**: Web application (frontend + backend)

**Performance Goals**: First streamed characters visible within 3s local (SC-001); visible multi-chunk streaming (SC-002)

**Constraints**:
- Real external LLM required (no stub for acceptance)
- Health = process listening only (`GET /info`)
- No stream cancel control
- Last 10 turns context window
- Env-based backend URL only

**Scale/Scope**: Single anonymous user, single thread, local/demo use

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Phase 0 | Post-Phase 1 | Notes |
|-----------|-------------|--------------|-------|
| I. Do not distribute by default | PASS (justified) | PASS | Two processes (browser + AgentOS) required by web architecture; no extra queues/services |
| II. Optimize for deletion | PASS | PASS | Small `backend/agent_os.py`, thin frontend runtime adapter |
| III. Explicit dependencies | PASS | PASS | LLM key, model, AgentOS URL via env; DI in agent factory |
| IV. Contract at boundary | PASS | PASS | `contracts/api-v1.md` v1.0.0 |
| V. Test transformation | PASS | PASS | Unit: slice/guards/reducer; integration: `/info`, `/runs` |
| VI. Structured events | PASS | PASS | Backend logs JSON with request_id on run/stream paths (implementation task) |
| VII. Recovery | PASS | PASS | Local dev revert = restart process; no prod deploy scope |
| VIII. Attention finite | N/A v1 | N/A v1 | No paging alerts in scope |
| IX. Value at user | PASS | PASS | quickstart defines shipped = runnable locally with observability |
| X. Commands discoverable | PASS | PASS | Root `Makefile` targets documented in quickstart |

**Gate result**: PASS — proceed to implementation tasks.

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-chat-app/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── api-v1.md        # Phase 1
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── agent_os.py          # AgentOS app: agent definition + serve entry
├── config.py            # Env-loaded settings (explicit deps)
├── cors.py              # CORS allowlist for local frontend
└── tests/
    ├── unit/
    │   └── test_context.py
    └── integration/
        └── test_health.py

frontend/
├── package.json
├── vite.config.ts
├── .env.example
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   └── assistant-ui/
│   │       └── thread.tsx
│   ├── runtime/
│   │   ├── AgentOSRuntimeProvider.tsx
│   │   ├── agentos-client.ts      # SSE fetch + parse
│   │   └── context-window.ts      # last-N slice (N=10)
│   └── lib/
│       └── env.ts                 # VITE_AGENTOS_URL
└── tests/
    └── context-window.test.ts

Makefile                   # dev, test, lint, health
```

**Structure Decision**: Standard web split (`frontend/` + `backend/`) with minimal files per Principle II. No Next.js BFF — frontend calls AgentOS directly with CORS to avoid an extra hop (Principle I).

## Complexity Tracking

> No unjustified constitution violations.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Phase 0 Output

See [research.md](./research.md) — all NEEDS CLARIFICATION items resolved:
- Backend: Agno AgentOS
- Frontend: assistant-ui ExternalStoreRuntime
- Health: `GET /info`
- Context N: 10 turns
- LLM: OpenAI via env

## Phase 1 Output

| Artifact | Path |
|----------|------|
| Data model | [data-model.md](./data-model.md) |
| API contract | [contracts/api-v1.md](./contracts/api-v1.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

## Implementation Notes (for `/speckit-tasks`)

1. **AgentOS setup**: Single agent `chat-agent` with TC system instructions; `stream=True` on runs; no `db`.
2. **assistant-ui**: Install Thread primitives; wire `useExternalStoreRuntime` with `isRunning` gate (disable send while streaming).
3. **SSE adapter**: Map AgentOS run events → append assistant text; handle errors on turn.
4. **CORS**: Allow frontend dev origin on AgentOS app.
5. **Env**: `VITE_AGENTOS_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `AGENT_OS_PORT`.
6. **Makefile**: `dev-backend`, `dev-frontend`, `dev`, `test`, `lint`, `health`.

## Next Command

`/speckit-tasks`
