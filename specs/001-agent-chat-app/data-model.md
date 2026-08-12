# Data Model: Agent Chat App (001)

**Date**: 2026-08-12  
**Persistence**: None for v1 (in-memory browser session only; no database)

## Overview

All entities exist in the browser for the active page session except ephemeral backend run metadata. AgentOS is configured **without** a database in v1 to satisfy FR-009.

**Context window constant**: `N = 10` message turns (see `research.md`).

---

## ChatThread

The single conversation container for one page session.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string (UUID) | yes | Generated once per page load; sent as AgentOS `session_id` for correlation only (not persisted server-side in v1) |
| `turns` | MessageTurn[] | yes | Ordered oldest → newest; full session transcript visible in UI |
| `status` | enum | yes | `idle` \| `streaming` \| `error` |

**State transitions**:

```text
idle → streaming   (user sends valid message)
streaming → idle   (stream completes successfully)
streaming → error  (stream fails mid-reply)
error → idle       (user sends next message after error displayed)
idle → idle        (empty send rejected; no transition)
```

**Invariants**:
- Exactly one thread per page session (FR-001, FR-005).
- `status = streaming` ⇒ send disabled (FR-014, edge case concurrent send).
- Refresh may discard thread (spec assumption).

---

## MessageTurn

One user or assistant contribution in the thread.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string (UUID) | yes | Stable for UI keys |
| `role` | enum | yes | `user` \| `assistant` |
| `content` | string | yes | UTF-8 text; Traditional Chinese expected for user input |
| `status` | enum | yes | `complete` \| `streaming` \| `error` |
| `createdAt` | ISO-8601 string | yes | Client clock |
| `errorMessage` | string | no | Set when `status = error` |

**Validation**:
- User turns: reject if `content` is empty or whitespace-only (FR-002, SC-006).
- Assistant turns: `content` may grow incrementally while `status = streaming` (FR-004).
- On stream failure: set `status = error`, keep partial `content` if any (edge case).

---

## StreamChunk

Ephemeral unit from AgentOS SSE while an assistant turn is open.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `turnId` | string | yes | Target assistant MessageTurn.id |
| `delta` | string | yes | Text fragment to append |
| `eventType` | string | yes | AgentOS event kind (e.g. content, completed, error) |
| `sequence` | integer | yes | Monotonic per turn for ordering |

**Lifecycle**: Discarded after applied to MessageTurn; not stored long-term.

---

## AgentRunRequest (boundary payload)

Frontend → AgentOS for each user send (derived, not stored).

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `agent_id` | string | yes | Constant `chat-agent` |
| `message` | string | yes | Latest user message text |
| `session_id` | string | yes | ChatThread.id |
| `stream` | boolean | yes | Always `true` for chat UI |
| `context_turns` | MessageTurn[] | yes | Last N=10 turns from thread **before** adding new user turn, or including new user turn per adapter design — must not exceed N |

**Note**: Because v1 has no server DB, multi-turn context is supplied by the frontend adapter (last-N slice), not AgentOS session history.

---

## ServiceStatus

Result of health/status check (User Story 3).

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `ready` | boolean | yes | `true` iff HTTP GET `/info` returns 2xx |
| `checkedAt` | ISO-8601 string | yes | Client or script timestamp |
| `baseUrl` | string | yes | From env-configured AgentOS URL |

**Invariant**: Missing/invalid LLM credentials do not affect `ready` (clarification: process listening only).

---

## Relationships

```text
ChatThread 1 ── * MessageTurn
MessageTurn (assistant, streaming) 1 ── * StreamChunk (ephemeral)
AgentRunRequest ──references──> last N MessageTurns + latest user message
ServiceStatus ──probes──> AgentOS /info
```

---

## Out of scope (v1)

- User accounts, auth tokens, tenant ids
- Durable storage, migrations, thread list
- Attachments, tool call entities, RAG document entities
- Server-side conversation archive
