# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`  
**User stack directive**: assistant-ui frontend, Agno SDK backend with AgentOS enabled  
**Revision**: Native **AG-UI** protocol — `@assistant-ui/react-ag-ui` ↔ Agno `AGUI` interface

## Summary

Build a minimal Traditional Chinese agent chat web app over the **AG-UI protocol**: assistant-ui (`useAgUiRuntime` + `HttpAgent`) on the frontend, Agno AgentOS with the **`AGUI` interface** on the backend (`POST /agui` streaming, `GET /status` health). One browser thread, real external LLM, env-configured AG-UI URL, no login/DB/RAG/tools/attachments/prod deploy. Context window **N = 10** turns trimmed client-side in `RunAgentInput.messages`.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)

**Primary Dependencies**:
- Backend: `agno[os,agui]`, `openai` (via Agno model)
- Frontend: `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, `@ag-ui/client`, React 19, Vite 6

**Storage**: N/A — session-only in browser (FR-009); AgentOS/agent without `db`; AG-UI messages carry context per run

**Testing**: pytest + httpx (`/status`); vitest (context trim); manual quickstart for E2E

**Target Platform**: Local dev — Linux/macOS; desktop browser

**Project Type**: Web application (frontend + backend)

**Performance Goals**: SC-001 first streamed chars ≤3s local; SC-002 visible multi-chunk streaming

**Constraints**:
- AG-UI wire protocol only (no custom SSE adapter)
- Real external LLM; health = `GET /status` listening check
- No stream cancel UI; N=10 turn context trim
- Env-based AG-UI endpoint URL

**Scale/Scope**: Single anonymous user, single thread, local/demo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Phase 0 | Post-Phase 1 (AG-UI revision) | Notes |
|-----------|-------------|-------------------------------|-------|
| I. Do not distribute by default | PASS | PASS | Browser + one AgentOS process; AG-UI removes need for BFF/proxy |
| II. Optimize for deletion | PASS | PASS | `agent_os.py` + `AgUiRuntimeProvider.tsx` + trim helper — no custom protocol code |
| III. Explicit dependencies | PASS | PASS | Env: `OPENAI_*`, `VITE_AGUI_URL`, `AGENT_OS_*` |
| IV. Contract at boundary | PASS | PASS | `contracts/ag-ui-v1.md` documents AG-UI + Agno mount points |
| V. Test transformation | PASS | PASS | Unit: trim; integration: `/status`; defer AG-UI parse tests to library |
| VI. Structured events | PASS | PASS | Backend JSON logs on AG-UI runs |
| VII. Recovery | PASS | PASS | Local restart |
| VIII. Attention finite | N/A | N/A | — |
| IX. Value at user | PASS | PASS | quickstart |
| X. Commands discoverable | PASS | PASS | Makefile |

**Gate result**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-chat-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ag-ui-v1.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── agent_os.py            # Agent + AgentOS + AGUI interface
├── config.py              # Env settings
└── tests/
    └── integration/
        └── test_status.py

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
│   │   ├── AgUiRuntimeProvider.tsx   # useAgUiRuntime + HttpAgent
│   │   └── trim-context.ts           # sliceLastNTurns(N=10)
│   └── lib/
│       └── env.ts                    # VITE_AGUI_URL
└── tests/
    └── trim-context.test.ts

Makefile
```

**Structure Decision**: Web split with **zero custom streaming layer** — AG-UI protocol connects assistant-ui and Agno directly (CORS on AgentOS only).

## Complexity Tracking

> No unjustified violations. Prior draft's custom SSE adapter removed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Phase 0 Output

See [research.md](./research.md):
- Protocol: AG-UI end-to-end
- Backend: AgentOS + `AGUI(agent=...)`
- Frontend: `useAgUiRuntime` + `HttpAgent`
- Health: `GET /status`
- Context: N=10 client trim

## Phase 1 Output

| Artifact | Path |
|----------|------|
| Data model | [data-model.md](./data-model.md) |
| API contract | [contracts/ag-ui-v1.md](./contracts/ag-ui-v1.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

## Implementation Notes (for `/speckit-tasks`)

1. **Backend**: `AgentOS(agents=[chat_agent], interfaces=[AGUI(agent=chat_agent)])`; TC instructions; no `db`.
2. **Frontend**: `HttpAgent({ url: env.VITE_AGUI_URL })` + `useAgUiRuntime({ agent })` + `Thread`.
3. **Context trim**: Wrap agent or intercept run input — keep last 10 turns in `messages`.
4. **Health**: `make health` → `curl -sf $AGENTOS_URL/status`.
5. **CORS**: Enable for frontend origin on AgentOS FastAPI app.
6. **No cancel UI**: Do not wire stop/cancel actions (FR-014).
7. **Env**: `VITE_AGUI_URL=http://localhost:7777/agui`, `OPENAI_API_KEY`, `OPENAI_MODEL`.

## Next Command

`/speckit-tasks`
