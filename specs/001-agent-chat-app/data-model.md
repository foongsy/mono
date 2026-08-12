# Data Model: Agent Chat App (001)

**Date**: 2026-08-12 (revised for AG-UI)  
**Persistence**: None for v1 (browser session only; no database)  
**Wire protocol**: AG-UI (`RunAgentInput` / event stream)

## Overview

Conversation state lives in assistant-ui runtime (browser memory). Backend is stateless for v1: each `POST /agui` receives trimmed messages in `RunAgentInput`. AgentOS runs without `db` (FR-009).

**Context window constant**: `N = 10` message turns.

---

## ChatThread

Single conversation container for one page session (assistant-ui thread).

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string (UUID) | yes | Maps to AG-UI `threadId`; generated per page load |
| `messages` | AgUiMessage[] | yes | Full session transcript for UI display |
| `isRunning` | boolean | yes | Managed by `useAgUiRuntime`; `true` during AG-UI run |

**State transitions** (driven by AG-UI events):

```text
isRunning false → true   (RUN_STARTED)
isRunning true → false   (RUN_FINISHED | RUN_ERROR | RUN_CANCELLED*)
```

*No user-triggered cancel in v1 (FR-014); `RUN_CANCELLED` not expected from UI.

**Invariants**:
- One thread per page session (FR-001, FR-005).
- `isRunning = true` ⇒ send disabled (FR-014).
- Refresh may discard thread (spec assumption).

---

## Message (AG-UI / assistant-ui)

Canonical message shape follows AG-UI protocol; assistant-ui `ThreadMessage` is the UI projection.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string | yes | Stable message id |
| `role` | enum | yes | `user` \| `assistant` \| `system` (system optional v1) |
| `content` | string or parts[] | yes | UTF-8; user input in Traditional Chinese |
| `status` | enum | yes (UI) | `complete` \| `streaming` \| `error` (assistant-ui derived) |

**Validation**:
- Empty/whitespace user content: rejected before `/agui` call (FR-002, SC-006).
- Assistant message streams via `TEXT_MESSAGE_*` events (FR-004).

---

## RunAgentInput (boundary payload)

Frontend → Agno `POST /agui` per send. Constructed by `@ag-ui/client` / `useAgUiRuntime`; trimmed by our adapter.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `threadId` | string | yes | ChatThread.id |
| `runId` | string | yes | Unique per send |
| `messages` | AgUiMessage[] | yes | **Last N=10 turns only** (FR-012) |
| `tools` | array | no | Omitted / empty (no tools v1) |

**Trim rule**: `messages = sliceLastNTurns(fullThreadMessages, 10)` immediately before run.

---

## AgUiEvent (stream)

Ephemeral events on `POST /agui` response stream. Parsed by `@assistant-ui/react-ag-ui` — not stored independently.

| Event types (v1) | Maps to |
|------------------|---------|
| `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_CHUNK` | Incremental assistant text |
| `RUN_STARTED` / `RUN_FINISHED` | Thread running state |
| `RUN_ERROR` | Turn error |

---

## ServiceStatus

Health check result (User Story 3).

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `ready` | boolean | yes | `true` iff `GET /status` returns 2xx |
| `checkedAt` | ISO-8601 | yes | Timestamp |
| `aguiUrl` | string | yes | From `VITE_AGUI_URL` |

**Invariant**: Invalid LLM credentials do not affect `ready` (process listening only).

---

## Relationships

```text
ChatThread 1 ── * Message (UI + RunAgentInput.messages subset)
RunAgentInput ──trim(N=10)──> subset of ChatThread.messages
POST /agui ──stream──> AgUiEvent* ──parsed by──> useAgUiRuntime
ServiceStatus ──probes──> GET /status
```

---

## Out of scope (v1)

- Server-side session DB, Agno `add_history_to_context` with storage
- Tool call entities, attachments, RAG documents
- Multi-thread list, auth, production deployment
