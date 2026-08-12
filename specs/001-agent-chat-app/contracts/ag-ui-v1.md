# AG-UI Contract: Agent Chat App v1

**Version**: 1.1.0  
**Date**: 2026-08-12  
**Protocol**: [AG-UI (Agent-User Interaction Protocol)](https://github.com/ag-ui-protocol/ag-ui)  
**Backend**: Agno AgentOS with `AGUI` interface  
**Frontend**: assistant-ui `@assistant-ui/react-ag-ui` + `@ag-ui/client` `HttpAgent`

## Overview

Frontend and backend communicate exclusively via AG-UI. Agno mounts the interface on AgentOS; assistant-ui's `useAgUiRuntime` consumes the event stream. **No custom SSE adapter or REST `/agents/{id}/runs` surface is used in v1.**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agui` | POST | Run agent — accepts `RunAgentInput`, streams AG-UI events |
| `/status` | GET | Health/status — process listening (FR-006) |

Default mount (no `AGUI.prefix`) at AgentOS base URL, e.g. `http://localhost:7777`.

---

## 1. Health / Status — `GET /status`

**Purpose**: FR-006, User Story 3

### Request

```http
GET /status HTTP/1.1
Host: localhost:7777
```

### Response

HTTP 2xx when AG-UI interface is mounted and process is listening.

### Semantics

| Condition | `ready` |
|-----------|---------|
| HTTP 2xx | `true` |
| Connection refused / timeout / non-2xx | `false` |
| Missing `OPENAI_API_KEY` | Still `true` if process responds 2xx |

---

## 2. Chat Run — `POST /agui`

**Purpose**: FR-003, FR-004 — streaming agent replies

### Request

`Content-Type: application/json` (AG-UI `RunAgentInput` per [ag-ui-protocol](https://github.com/ag-ui-protocol/ag-ui))

Key fields (v1 subset):

| Field | Required | Description |
|-------|----------|-------------|
| `threadId` | yes | Client thread id (UUID, session-scoped) |
| `runId` | yes | Unique run id per send |
| `messages` | yes | Conversation messages (AG-UI message format) |
| `state` | no | Opaque agent state (unused v1) |
| `tools` | no | Empty / omitted (no tools v1) |
| `context` | no | Omitted v1 |
| `forwardedProps` | no | Optional metadata |

**Context window (FR-012)**: Frontend MUST trim `messages` to the last **N=10** turns before each run. Full transcript may remain in assistant-ui UI state.

### Response

`Content-Type: text/event-stream` — AG-UI event stream.

Events consumed by `@assistant-ui/react-ag-ui` (v1 subset):

| Event | Effect |
|-------|--------|
| `RUN_STARTED` | Thread `isRunning = true` |
| `TEXT_MESSAGE_START` / `TEXT_MESSAGE_CONTENT` / `TEXT_MESSAGE_END` | Streaming assistant text (FR-004) |
| `TEXT_MESSAGE_CHUNK` | Incremental text delta |
| `RUN_FINISHED` | Run complete; `isRunning = false` |
| `RUN_ERROR` | Error on turn; `isRunning = false` |

### Error semantics

| Condition | Client behavior |
|-----------|-----------------|
| LLM / provider error | `RUN_ERROR`; show error on turn |
| Network failure | Protocol error / `onError`; partial text retained |
| Empty user message | Client MUST NOT call `/agui` (FR-002) |

---

## 3. Backend setup (Agno)

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

chat_agent = Agent(
    id="chat-agent",
    model=OpenAIChat(id=os.environ["OPENAI_MODEL"]),
    instructions="...",  # Prefer Traditional Chinese (FR-013)
)

agent_os = AgentOS(
    agents=[chat_agent],
    interfaces=[AGUI(agent=chat_agent)],
)
app = agent_os.get_app()
```

Install: `uv pip install 'agno[os,agui]' openai`

---

## 4. Frontend setup (assistant-ui)

```tsx
import { HttpAgent } from "@ag-ui/client";
import { useAgUiRuntime } from "@assistant-ui/react-ag-ui";
import { AssistantRuntimeProvider } from "@assistant-ui/react";

const agent = new HttpAgent({
  url: import.meta.env.VITE_AGUI_URL, // e.g. http://localhost:7777/agui
  headers: { Accept: "text/event-stream" },
});

const runtime = useAgUiRuntime({ agent, showThinking: false });
```

Install: `npm install @assistant-ui/react @assistant-ui/react-ag-ui @ag-ui/client`

Apply `sliceLastNTurns(messages, 10)` at run boundary (wrapper or hook) before `HttpAgent` sends input.

---

## 5. CORS

AgentOS MUST allow frontend dev origin for `GET /status` and `POST /agui`.

---

## 6. Environment variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `VITE_AGUI_URL` | yes | `http://localhost:7777/agui` | Full AG-UI run endpoint URL (FR-007) |
| `OPENAI_API_KEY` | yes (for chat) | `sk-...` | LLM credentials (FR-011) |
| `OPENAI_MODEL` | no | `gpt-4o-mini` | Model id |
| `AGENT_OS_HOST` | no | `0.0.0.0` | Bind host |
| `AGENT_OS_PORT` | no | `7777` | Bind port |

Alternative: `VITE_AGENTOS_URL=http://localhost:7777` with frontend appending `/agui` — document one canonical approach in implementation.

---

## 7. Versioning

| Version | Change |
|---------|--------|
| 1.0.0 | Initial draft (AgentOS REST `/runs` — superseded) |
| 1.1.0 | AG-UI native integration (`/agui`, `/status`) |

Breaking changes to paths, required `RunAgentInput` fields, or event types → MAJOR bump.

Semantic reconciliation at boundary: `@assistant-ui/react-ag-ui` owns frontend parsing; Agno `AGUI` owns backend emission (Principle IV).
