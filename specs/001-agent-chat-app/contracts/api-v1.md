# API Contract: Agent Chat App v1

**Version**: 1.0.0  
**Date**: 2026-08-12  
**Backend**: Agno AgentOS  
**Frontend env**: `NEXT_PUBLIC_AGENTOS_URL` or `VITE_AGENTOS_URL` (base URL, no trailing slash)

All paths are relative to the configured base URL.

---

## 1. Health / Status — `GET /info`

**Purpose**: FR-006, User Story 3 — process listening check (no LLM probe).

### Request

```http
GET /info HTTP/1.1
Host: localhost:7777
```

No auth required when `auth_mode=none` (v1 default).

### Response `200 OK`

```json
{
  "auth_mode": "none",
  "agent_count": 1,
  "team_count": 0,
  "workflow_count": 0,
  "agno_version": "string"
}
```

### Semantics

| Condition | Client interpretation |
|-----------|----------------------|
| HTTP 2xx | `ready = true` (ServiceStatus) |
| Connection refused / timeout / non-2xx | `ready = false` |
| Missing LLM API key | Still `ready = true` if process responds 2xx |

---

## 2. Chat Stream — `POST /agents/{agent_id}/runs`

**Purpose**: FR-003, FR-004 — stream agent reply to web UI.

**Path parameter**: `agent_id = chat-agent` (fixed for v1)

### Request

```http
POST /agents/chat-agent/runs HTTP/1.1
Host: localhost:7777
Content-Type: application/x-www-form-urlencoded
Accept: text/event-stream

message=<url-encoded user text>
&session_id=<uuid>
&stream=true
```

| Field | Required | Description |
|-------|----------|-------------|
| `message` | yes | Latest user message (Traditional Chinese) |
| `session_id` | yes | Client thread id (correlation only in v1) |
| `stream` | yes | Must be `true` for streaming UI |

**Context window (FR-012)**: v1 frontend applies last **N=10** turns client-side. If AgentOS native session history is enabled later, contract version must bump. For v1 without DB, the adapter MAY prepend recent turns into `message` or pass via supported metadata fields — implementation detail in tasks; acceptance is behavioral (agent aware of recent window per spec).

### Response `200 OK` (SSE)

`Content-Type: text/event-stream`

Events follow AgentOS run streaming format. Frontend adapter MUST:

1. Parse SSE frames
2. Extract text content deltas from content events
3. Append deltas to the in-progress assistant turn until completion or error event
4. Mark turn complete on terminal event

### Error responses

| Condition | Expected client behavior |
|-----------|-------------------------|
| LLM auth failure / provider error | Show error on assistant turn; allow next send after idle |
| Network failure mid-stream | Show error on assistant turn with partial text if any |
| Empty message (client-side) | Do not call endpoint (FR-002) |

---

## 3. CORS (browser direct access)

AgentOS MUST allow the frontend dev origin (e.g. `http://localhost:5173`) for:

- `GET /info`
- `POST /agents/chat-agent/runs`

Methods: `GET`, `POST`  
Headers: `Content-Type`, `Accept`

---

## 4. Frontend configuration contract

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_AGENTOS_URL` or `VITE_AGENTOS_URL` | yes | `http://localhost:7777` | AgentOS base URL (FR-007) |

Changing this variable and restarting/reloading frontend MUST be sufficient to retarget backend (SC-005).

---

## 5. Versioning policy

- **1.0.0**: Initial v1 contract (this document)
- Breaking changes (path, required fields, event shape) → MAJOR bump
- Additive optional fields → MINOR bump

Semantic reconciliation at boundary owned by frontend adapter (Principle IV).
