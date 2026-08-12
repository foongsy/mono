# Research: Agent Chat App (001)

**Date**: 2026-08-12  
**Feature**: `specs/001-agent-chat-app/spec.md`  
**User directive**: assistant-ui frontend, Agno SDK backend with AgentOS enabled

## 1. Backend runtime — Agno AgentOS

**Decision**: Run a single Agno `AgentOS` FastAPI app exposing one chat agent (`id="chat-agent"`) on default port `7777`.

**Rationale**:
- Spec requires real external LLM streaming, health/status, and a backend agent — AgentOS provides `POST /agents/{agent_id}/runs` with SSE streaming out of the box.
- Constitution Principle I: one backend deployable; AgentOS bundles agent + HTTP server without extra microservices.
- Clarification: health = process listening → `GET /info` (public metadata) satisfies acceptance without LLM probe.

**Alternatives considered**:
- Raw FastAPI + manual OpenAI streaming — rejected; duplicates AgentOS run/stream plumbing.
- AgentOS with SQLite `db` — rejected for v1; spec FR-009 forbids database-backed chat persistence. AgentOS runs without `db` for v1; transcript lives in the browser.

**Key implementation notes**:
- `from agno.os import AgentOS` + `agent_os.get_app()` / `agent_os.serve()`.
- Agent model via env (`OPENAI_API_KEY`, model id env); instructions enforce Traditional Chinese replies.
- Run endpoint: `POST /agents/chat-agent/runs` with `Content-Type: application/x-www-form-urlencoded`, `stream=true`.
- Health/status for v1: `GET /info` returns 200 when process is listening (maps to FR-006 / User Story 3).
- Enable CORS on AgentOS for local frontend origin (browser → AgentOS direct calls).

## 2. Frontend UI — assistant-ui

**Decision**: React SPA (Vite) with `@assistant-ui/react`, `@assistant-ui/react-markdown`, and `useExternalStoreRuntime` wired to AgentOS SSE.

**Rationale**:
- User requested assistant-ui explicitly.
- Agno AgentOS speaks form-urlencoded SSE, not Vercel AI SDK UI streams — `useChatRuntime` / `@assistant-ui/react-ai-sdk` targets AI SDK backends and would force an unnecessary BFF.
- `useExternalStoreRuntime` gives full control over streaming updates, send-disable during in-flight reply (FR-014), and session-only message state (FR-009).

**Alternatives considered**:
- `@assistant-ui/react-ai-sdk` + Next.js API proxy — rejected; adds a Node hop and AI SDK translation layer without v1 benefit.
- `@assistant-ui/react-data-stream` — viable but ExternalStore maps cleanly to manual SSE chunk append for AgentOS events.
- Plain React chat UI — rejected; user specified assistant-ui.

**Key implementation notes**:
- Prebuilt `Thread` component from assistant-ui starter patterns.
- `NEXT_PUBLIC_AGENTOS_URL` (or `VITE_AGENTOS_URL`) configures backend base URL (FR-007).
- Single thread: one runtime provider instance, no thread list UI.
- No stop/cancel button (clarification B).

## 3. Context window N

**Decision**: **N = 10 message turns** (counting both user and assistant messages).

**Rationale**:
- Spec requires a small fixed integer at planning time (FR-012).
- 10 turns ≈ five exchanges — enough for P2 multi-turn demos without unbounded token growth.
- Frontend slices `messages.slice(-N)` before each AgentOS call; full transcript remains in UI state.

**Alternatives considered**:
- N = 6 (three exchanges) — too tight for “depends on recent context” acceptance tests.
- N = 20 — acceptable but larger LLM cost for v1 with no benefit stated in spec.
- Server-side session history via AgentOS DB — rejected (no DB in v1).

## 4. Streaming protocol mapping

**Decision**: Browser `fetch` + `ReadableStream` (or `EventSource` if compatible) parses AgentOS SSE; map `RunContentEvent` text chunks to incremental assistant-ui message updates.

**Rationale**:
- AgentOS documents SSE by default on run endpoints (`curl -N ... stream=true`).
- assistant-ui ExternalStore expects caller to append partial assistant content while `isRunning=true`.

**Alternatives considered**:
- WebSocket — not AgentOS default; unnecessary.

## 5. LLM provider

**Decision**: OpenAI-compatible model via Agno `OpenAIChat` (or `OpenAIResponses`) with model id from `OPENAI_MODEL` env defaulting to `gpt-4o-mini`.

**Rationale**:
- Clarification requires real external LLM; OpenAI is Agno’s primary documented path.
- Credentials only via env (FR-011).
- `gpt-4o-mini` is cost-effective for v1 local demos with strong Traditional Chinese support.

**Alternatives considered**:
- Anthropic / other providers — supported by Agno but deferred; env-swappable later without spec change.

## 6. Testing strategy

**Decision**:
- **Unit**: pure functions — context window slice, empty-message guard, SSE chunk reducer.
- **Integration**: httpx/pytest against AgentOS `/info` and `/agents/chat-agent/runs` (stream=false smoke with mocked LLM or recorded fixture if CI lacks keys).
- **E2E manual**: quickstart scenarios (SC-001–SC-007).

**Rationale**: Constitution Principle V — test transformations and boundaries, not framework wiring.

## 7. Command surface (Constitution X)

**Decision**: Root `Makefile` with `dev-backend`, `dev-frontend`, `dev`, `test`, `lint`, `health` — same targets documented in quickstart and used by CI.

**Rationale**: Principle X requires discoverable, identical local/CI commands.
