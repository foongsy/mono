# Research: Agent Chat App (001)

**Date**: 2026-08-12 (revised)  
**Feature**: `specs/001-agent-chat-app/spec.md`  
**User directive**: assistant-ui frontend, Agno SDK backend with AgentOS enabled  
**Revision**: Use native **AG-UI** protocol on both sides — no custom SSE adapter

## 1. Integration protocol — AG-UI (Agent-User Interaction)

**Decision**: Connect frontend and backend via the [AG-UI protocol](https://github.com/ag-ui-protocol/ag-ui) end-to-end.

**Rationale**:
- Both stacks ship first-class AG-UI support:
  - **Agno**: `from agno.os.interfaces.agui import AGUI` mounted on AgentOS → `POST /agui`, `GET /status`
  - **assistant-ui**: `@assistant-ui/react-ag-ui` + `@ag-ui/client` `HttpAgent` + `useAgUiRuntime`
- Eliminates custom SSE parsing, manual message append logic, and protocol translation (Principle II).
- Streaming (`TEXT_MESSAGE_*`), run lifecycle (`RUN_STARTED` / `RUN_FINISHED` / `RUN_ERROR`), and errors are handled by the runtime adapter.

**Alternatives considered** (rejected in prior draft):
- `useExternalStoreRuntime` + manual AgentOS `/agents/{id}/runs` SSE — reinventing wire protocol already solved by AG-UI.
- Next.js BFF translating AI SDK ↔ AgentOS — extra hop, wrong protocol.

**Key implementation notes**:
- Backend install: `uv pip install 'agno[os,agui]' openai`
- Backend wiring:
  ```python
  agent_os = AgentOS(
      agents=[chat_agent],
      interfaces=[AGUI(agent=chat_agent)],
  )
  ```
- Frontend install: `npm install @assistant-ui/react @assistant-ui/react-ag-ui @ag-ui/client`
- Frontend wiring:
  ```tsx
  const agent = new HttpAgent({ url: `${baseUrl}/agui` });
  const runtime = useAgUiRuntime({ agent });
  ```
- Reference: [assistant-ui AG-UI quickstart](https://www.assistant-ui.com/docs/runtimes/ag-ui/quickstart), [Agno AG-UI interface](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction)

## 2. Backend runtime — Agno AgentOS + AGUI interface

**Decision**: Single AgentOS app with one agent and one `AGUI` interface (default prefix → `/agui`, `/status`).

**Rationale**:
- Spec requires AgentOS-backed agent, streaming, health endpoint, real LLM.
- `GET /status` is the AG-UI health/status surface (maps directly to FR-006 / User Story 3 clarification: process listening, no LLM probe).
- No `db` on AgentOS or agent for v1 (FR-009); conversation state lives in the browser; AG-UI `RunAgentInput.messages` carries context each run.

**Alternatives considered**:
- AgentOS REST `/agents/{id}/runs` without AGUI interface — lower-level; bypasses the shared protocol assistant-ui expects.
- AgentOS with SQLite — rejected (FR-009).

**Key implementation notes**:
- Agent instructions: prefer Traditional Chinese replies (FR-013).
- LLM via env: `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`).
- CORS: allow `http://localhost:5173` (and `http://127.0.0.1:5173`) on AgentOS for browser `HttpAgent` calls.
- Structured logging on `/agui` runs (Principle VI) with `request_id` (may equal `run_id`), `thread_id`, and `run_id`.

## 3. Frontend UI — assistant-ui + react-ag-ui

**Decision**: React SPA (Vite) with assistant-ui `Thread` + `useAgUiRuntime({ agent: HttpAgent })`.

**Rationale**:
- User requested assistant-ui; `@assistant-ui/react-ag-ui` is the purpose-built adapter for AG-UI backends including Agno.
- Runtime handles streaming text, run state (`isRunning`), and errors — satisfies FR-004, concurrent-send disable via thread `isRunning` (FR-014).
- Single thread: default runtime, no `adapters.threadList` (spec: one thread v1).

**Alternatives considered**:
- `useExternalStoreRuntime` — unnecessary when AG-UI runtime exists.
- `@assistant-ui/react-ai-sdk` — wrong protocol (Vercel AI SDK, not AG-UI).

**Key implementation notes**:
- Env: **`VITE_AGUI_URL` only** (full URL to `POST /agui`, e.g. `http://localhost:7777/agui`) — FR-007. Do not introduce `VITE_AGENTOS_URL`.
- Do not expose cancel/stop UI controls (clarification: no stop in v1); rely on runtime `isRunning` to disable send.
- Optional: `showThinking: false` for simpler v1 UI (no tools/RAG).
- Thread: use assistant-ui `Thread` without composer cancel/stop actions (omit stop button from starter chrome).

## 4. Context window N = 10 turns

**Decision**: Client-side trim via **`TrimmingHttpAgent`** (`frontend/src/runtime/trimming-http-agent.ts`) wrapping `@ag-ui/client` `HttpAgent`. Before each run request, set `messages = sliceLastNTurns(messages, 10)`. Full transcript remains in assistant-ui thread UI.

**Rationale**:
- Spec FR-012 + clarification: last N turns, N fixed at planning.
- Without server DB, context MUST travel in `RunAgentInput.messages` each request — AG-UI's default behavior.
- Extending/wrapping `HttpAgent` is the stable interception point; do not depend on undocumented `useAgUiRuntime` internals.

**Alternatives considered**:
- Undocumented runtime hook / `runConfig` — rejected; API not stable for v1.
- Agno `num_history_messages=10` with DB — requires DB (FR-009 violation).
- Server-side trim in custom FastAPI middleware — unnecessary; client owns transcript in v1.

## 5. Health / status endpoint

**Decision**: Use AG-UI interface `GET /status` (not AgentOS `GET /info`).

**Rationale**:
- Native health endpoint for the AG-UI surface the frontend actually uses.
- Meets clarification: reports interface/process readiness without LLM connectivity check.
- `make health` curls `{baseUrl}/status`.

## 6. LLM provider

**Decision**: OpenAI via Agno `OpenAIChat` or `OpenAIResponses`; model from `OPENAI_MODEL` env.

**Rationale**: Clarification requires real external LLM; credentials via env only (FR-011).

## 7. Testing strategy

**Decision**:
- **Unit**: `sliceLastNTurns` (N=10), empty-message guard (assistant-ui input validation).
- **Integration**: httpx against `GET /status`; AG-UI run smoke via `@ag-ui/client` or recorded SSE fixture.
- **Manual**: quickstart scenarios SC-001–SC-007.

**Rationale**: Test our trim transform and protocol boundaries; do not re-test AG-UI event parsing (owned by `@assistant-ui/react-ag-ui`).

## 8. Command surface (Constitution X)

**Decision**: Root `Makefile` — `dev-backend`, `dev-frontend`, `dev`, `test`, `lint`, `health` (curl `/status`).

**Rationale**: Principle X — identical local/CI commands.
