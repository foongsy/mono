# Feature Specification: Agent Chat App

**Feature Branch**: `001-agent-chat-app`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "建立一個簡單的 agent chat app。使用者可在 web 介面輸入繁體中文訊息，並收到由 backend agent 串流回傳的回覆。v1 只需要單一聊天 thread；不包含登入、資料庫、RAG、tools、上傳附件或 production deployment。Acceptance criteria：1. web 介面可送出訊息並顯示串流回覆。2. backend 有可檢查的 health/status endpoint。3. 前端 endpoint 可透過 environment variable 設定。"

## Clarifications

### Session 2026-08-12

- Q: For v1 acceptance, what should produce the agent’s streamed reply? → A: Real external LLM required for v1 acceptance (credentials configured outside the app)
- Q: When the user sends a follow-up message in the same thread, what conversation context should the agent receive? → A: Only the last N turns (fixed small window; N chosen at planning)
- Q: When should the health/status endpoint report the backend as ready? → A: Process is listening (no LLM config/connectivity check)
- Q: What language should the agent’s replies use when the user writes in Traditional Chinese? → A: Prefer Traditional Chinese replies for Traditional Chinese user input

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send a message and see a streaming reply (Priority: P1)

A user opens the web chat interface, types a Traditional Chinese message into the input, sends it, and watches the agent's reply appear progressively (streaming) in the same conversation view until the reply is complete.

**Why this priority**: This is the only core user value of v1. Without send + stream display, the product does not exist.

**Independent Test**: Open the web UI, send one Traditional Chinese message, and confirm the reply text appears incrementally in the single thread without refresh.

**Acceptance Scenarios**:

1. **Given** the chat UI is open with an empty thread, **When** the user submits a Traditional Chinese message, **Then** the message appears in the thread as a user turn and a streaming agent reply begins without a full page reload.
2. **Given** an agent reply is streaming, **When** new text chunks arrive, **Then** the UI appends them to the in-progress agent message so the user sees progressive output.
3. **Given** an agent reply has finished streaming, **When** the user views the thread, **Then** the complete user message and complete agent reply remain visible in order in the single thread.

---

### User Story 2 - Continue the same thread (Priority: P2)

After at least one exchange, the user sends another Traditional Chinese message in the same page session and receives another streaming reply in the same single thread, with prior turns still visible. The agent uses only a fixed recent window of turns (last N turns) as context, not necessarily the entire thread history.

**Why this priority**: Multi-turn conversation in one thread is required by "單一聊天 thread," but a first successful exchange (P1) already delivers MVP value.

**Independent Test**: Send two messages in sequence without leaving the page; confirm both pairs of turns remain visible and ordered, and that a follow-up that depends on recent prior context is answered with awareness of that recent window.

**Acceptance Scenarios**:

1. **Given** the thread already shows at least one user/agent exchange, **When** the user sends another Traditional Chinese message, **Then** the new message and its streaming reply are appended below the existing turns in the same thread.
2. **Given** multiple turns exist in the session, **When** the user scrolls the conversation, **Then** earlier turns remain available in that single thread (no second thread is created).
3. **Given** the thread contains more turns than the context window N, **When** the user sends a new message, **Then** the agent is only required to use the most recent N turns as context (older turns remain visible in the UI but need not be sent to the agent).

---

### User Story 3 - Verify service readiness (Priority: P3)

A developer or operator checks a backend health/status endpoint and learns whether the chat backend process is reachable and listening. Readiness here does not imply LLM credentials or connectivity are valid.

**Why this priority**: Required for local verification and acceptance criterion 2; not part of the end-user chat journey.

**Independent Test**: Call the health/status endpoint while the backend is running and confirm a clear ready/listening signal; stop the backend and confirm the check fails or reports unready. Missing LLM credentials alone MUST NOT make this endpoint report unready.

**Acceptance Scenarios**:

1. **Given** the backend process is running and listening, **When** someone requests the health/status endpoint, **Then** the response indicates a healthy/ready (listening) state in a machine-checkable way — even if LLM credentials are missing or invalid.
2. **Given** the backend process is not running, **When** someone requests the health/status endpoint, **Then** the check fails to obtain a healthy/ready response.

---

### Edge Cases

- What happens when the user submits an empty or whitespace-only message? The system MUST reject the send and MUST NOT create an empty user turn or start a stream.
- What happens when the agent stream fails or disconnects mid-reply? The UI MUST show a clear error on that turn and MUST allow the user to send a new message afterward.
- What happens when the user tries to send another message while a reply is still streaming? The system MUST prevent concurrent sends for the single thread (disable send or queue rejection) until the in-flight reply completes or fails.
- What happens when the configured frontend backend address is wrong or unreachable? The UI MUST show a clear connection/error state when send is attempted (and health checks fail as in User Story 3).
- What happens when the external LLM is unreachable, rejects credentials, or returns an error? The UI MUST show a clear error on that turn; the backend MUST NOT pretend the reply succeeded.
- What happens on page refresh? Conversation history for v1 is session-only and MAY be lost; no durable restore is required.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to open a web chat interface that presents a single conversation thread.
- **FR-002**: Users MUST be able to enter Traditional Chinese text as a chat message and submit it.
- **FR-013**: When the user message is primarily Traditional Chinese, the agent SHOULD reply in Traditional Chinese. Occasional mixed scripts or proper nouns do not by themselves fail acceptance; a wholly unrelated-language reply for a clear Traditional Chinese prompt does fail the language preference expectation.
- **FR-003**: The system MUST send submitted messages to a backend agent backed by a real external LLM and return the agent's reply as a stream of text updates to the web interface.
- **FR-011**: LLM credentials and provider access MUST be supplied via external configuration (for example environment variables) outside application source; v1 acceptance MUST NOT rely on a stub or echo agent in place of the real LLM.
- **FR-004**: The web interface MUST display the user's message and the agent's streaming reply in the same single thread, updating the reply progressively as stream chunks arrive.
- **FR-005**: The system MUST support multiple sequential turns within that one thread during a single browser page session.
- **FR-012**: When invoking the agent for a new user message, the system MUST supply only the last N message turns from the thread as model context (a fixed small window). The concrete value of N is chosen during planning and MUST be documented; turns older than the window MAY remain visible in the UI but MUST NOT be required in the agent context.
- **FR-006**: The backend MUST expose a health/status endpoint that reports whether the backend process is listening. This endpoint MUST NOT require a successful LLM configuration or connectivity check to report ready.
- **FR-007**: The web interface MUST obtain the backend base address (or chat endpoint address) from an environment variable so the same frontend build can target different backend locations without code changes.
- **FR-008**: The system MUST NOT require user login or authentication in v1.
- **FR-009**: The system MUST NOT require a database for chat persistence in v1.
- **FR-010**: The system MUST NOT include RAG, agent tools, file/attachment upload, or production deployment workflows in v1.

### Key Entities

- **Chat Thread**: The single conversation container visible in the UI for a page session; v1 allows exactly one thread per session. The UI may show the full session transcript while the agent only receives the last N turns.
- **Context Window (N turns)**: The fixed maximum number of most recent message turns sent to the agent on each request; N is a planning-time constant for v1.
- **Message Turn**: One contribution in the thread — either from the user or from the agent — with ordered content; agent turns may be incomplete while streaming.
- **Stream Chunk**: A partial piece of an agent reply delivered over time until the turn is complete or failed.
- **Service Status**: The listening/not-listening signal exposed by the health/status endpoint (process liveness only; not LLM readiness).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can open the chat UI, submit a Traditional Chinese message, and see the first streamed reply characters appear on screen within 3 seconds under normal local-network conditions (once the agent has begun responding).
- **SC-002**: During a successful reply, the user can observe at least two distinct UI updates of the agent message content before the reply is marked complete (streaming is visible, not only a single final dump), except when the full reply is shorter than what would produce multiple chunks.
- **SC-003**: A user can complete two full exchanges (user message + completed agent reply) in the same thread without creating a second thread or leaving the page.
- **SC-004**: 100% of health/status checks against a running listening backend return a healthy/ready (listening) indication; checks against a stopped backend do not return healthy/ready. Missing LLM credentials alone do not cause a failing health/status result while the process is listening.
- **SC-005**: Changing only the documented frontend environment variable and restarting/reloading as required is sufficient to point the UI at a different backend address — no source edits required.
- **SC-007**: In manual verification with clear Traditional Chinese prompts, agent replies are predominantly Traditional Chinese (preferred language), not a wholly different natural language.

## Assumptions

- Target users are developers or demo viewers using a desktop browser on a local or trusted network.
- "串流回覆" means progressive delivery of reply text to the UI as it is produced, not a single all-at-once response after full generation (though very short replies may complete in one update).
- The backend agent uses a real external LLM that can accept Traditional Chinese input and SHOULD produce Traditional Chinese replies for Traditional Chinese prompts; exact model/provider choice is deferred to planning, but a stub/echo agent is not acceptable for v1 acceptance.
- LLM API credentials are provided by the operator/developer outside the app codebase; missing or invalid credentials cause chat send/stream failures with a clear UI error, but do not by themselves make the health/status endpoint report unready.
- v1 uses one anonymous single-thread session scoped to the browser page; refresh may clear history.
- Agent context for each request is the last N turns only; full-history context is out of scope for v1. Exact N is deferred to planning but MUST be a small fixed integer.
- No multi-user isolation, sharing, export, or thread list is required.
- Health/status means process listening only; it is for human and scripted checks during development and is not an LLM dependency probe. Public SLA/monitoring dashboards are out of scope (constitution observability applies when implementing, but production ops are excluded from this feature).
- Frontend "endpoint via environment variable" applies to how the web app is configured at build or runtime for local/dev use — not to production secret management.
- Out of scope remains binding: no login, database, RAG, tools, attachments, or production deployment work in this feature.
