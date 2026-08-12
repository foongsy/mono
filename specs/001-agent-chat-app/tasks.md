# Tasks: Agent Chat App

**Input**: Design documents from `/specs/001-agent-chat-app/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ag-ui-v1.md, quickstart.md

**Tests**: Included for plan-specified unit/integration coverage (`trim-context`, `GET /status`); E2E remains manual via quickstart.md

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/`
- Frontend: `frontend/`
- Root: `Makefile`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding and dependency baselines for Agno AgentOS + assistant-ui AG-UI stack

- [ ] T001 Create directory tree `backend/`, `backend/tests/integration/`, `frontend/src/components/assistant-ui/`, `frontend/src/runtime/`, `frontend/src/lib/`, `frontend/tests/` per plan.md
- [ ] T002 Initialize Python project with `agno[os,agui]` and `openai` in `backend/pyproject.toml` (`openai` required by Agno `OpenAILike` for Vercel AI Gateway)
- [ ] T003 [P] Initialize Vite + React + TypeScript app with `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, and `@ag-ui/client` in `frontend/package.json`
- [ ] T004 [P] Add root `Makefile` with targets `dev-backend`, `dev-frontend`, `dev`, `test`, `lint`, `health` (`health` = `curl -sf` to `http://$${AGENT_OS_HOST:localhost}:$${AGENT_OS_PORT:7777}/status`)
- [ ] T005 [P] Add `backend/.env.example` with `AI_GATEWAY_API_KEY`, `LLM_MODEL_ID=google/gemini-3.5-flash-lite`, optional `AI_GATEWAY_BASE_URL=https://ai-gateway.vercel.sh/v1`, `AGENT_OS_HOST`, `AGENT_OS_PORT` and `frontend/.env.example` with **`VITE_AGUI_URL` only** (example `http://localhost:7777/agui`)
- [ ] T006 [P] Add `.gitignore` entries for `backend/.env`, `frontend/.env.local`, `node_modules/`, `__pycache__/`, `.venv/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared config, AgentOS+AGUI shell, CORS, frontend shell, env wiring — must complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Implement env settings loader in `backend/config.py` (read `AI_GATEWAY_API_KEY`, `LLM_MODEL_ID` default `google/gemini-3.5-flash-lite`, `AI_GATEWAY_BASE_URL` default `https://ai-gateway.vercel.sh/v1`, `AGENT_OS_HOST`, `AGENT_OS_PORT`; no import-time side effects)
- [ ] T008 Create AgentOS app with chat agent and `AGUI` interface (no `db`) in `backend/agent_os.py`
- [ ] T009 Enable CORS allowlist for `http://localhost:5173` and `http://127.0.0.1:5173` on the AgentOS FastAPI app in `backend/agent_os.py`
- [ ] T010 Add structured JSON logging on AG-UI runs with `request_id` (may equal `run_id`), `thread_id`, and `run_id` in `backend/agent_os.py`
- [ ] T011 [P] Implement **`VITE_AGUI_URL` only** reader (reject missing URL) in `frontend/src/lib/env.ts`
- [ ] T012 [P] Create Vite entry and root shell in `frontend/src/main.tsx` and `frontend/src/App.tsx`
- [ ] T013 Wire `Makefile` `dev-backend` / `dev-frontend` to AgentOS serve and Vite; keep single `health` target from T004 pointing at `/status`

**Checkpoint**: Backend serves AgentOS+AGUI; frontend boots; env URLs configurable — story work can begin

---

## Phase 3: User Story 1 - Send a message and see a streaming reply (Priority: P1) 🎯 MVP

**Goal**: User opens web chat, sends Traditional Chinese text, sees AG-UI streamed assistant reply in one thread

**Independent Test**: Open UI, send one TC message, confirm incremental assistant text without page reload (quickstart Scenario 2)

### Implementation for User Story 1

- [ ] T014 [US1] Configure chat agent Traditional Chinese reply instructions and Vercel AI Gateway model via Agno `OpenAILike` (`id`/`api_key`/`base_url` from env) in `backend/agent_os.py`
- [ ] T015 [P] [US1] Create assistant-ui `Thread` in `frontend/src/components/assistant-ui/thread.tsx` using starter primitives **without** Stop/Cancel composer actions (omit stop button from default chrome)
- [ ] T016 [US1] Implement `useAgUiRuntime` provider with `showThinking: false` in `frontend/src/runtime/AgUiRuntimeProvider.tsx` (agent instance supplied later by T023; for US1 may use plain `HttpAgent` temporarily if needed, then swap)
- [ ] T017 [US1] Mount `AgUiRuntimeProvider` and `Thread` in `frontend/src/App.tsx` using `VITE_AGUI_URL` from `frontend/src/lib/env.ts`
- [ ] T018 [US1] Reject empty/whitespace-only sends in `frontend/src/runtime/AgUiRuntimeProvider.tsx` before starting a run (no new turn, no `/agui` call)
- [ ] T019 [US1] Disable send while runtime `isRunning` and ensure no cancel/stop control is rendered (FR-014) in `frontend/src/components/assistant-ui/thread.tsx`
- [ ] T020 [US1] Wire `onError` on `useAgUiRuntime` to surface stream/LLM errors on the assistant turn and allow a subsequent send after idle in `frontend/src/runtime/AgUiRuntimeProvider.tsx`

**Checkpoint**: US1 MVP — one-shot TC chat with streaming AG-UI reply works end-to-end

---

## Phase 4: User Story 2 - Continue the same thread (Priority: P2)

**Goal**: Multi-turn chat in the same page session; agent receives only last N=10 turns while UI keeps full transcript

**Independent Test**: Two sequential exchanges without leaving page; follow-up uses recent context; older-than-N turns stay visible (quickstart Scenario 3)

### Implementation for User Story 2

- [ ] T021 [P] [US2] Implement `sliceLastNTurns(messages, 10)` pure helper in `frontend/src/runtime/trim-context.ts`
- [ ] T022 [P] [US2] Add unit tests for `sliceLastNTurns` (empty, &lt;N, exactly N, &gt;N) in `frontend/tests/trim-context.test.ts`
- [ ] T023 [US2] Implement `TrimmingHttpAgent` in `frontend/src/runtime/trimming-http-agent.ts` wrapping `@ag-ui/client` `HttpAgent` to apply `sliceLastNTurns(..., 10)` on `RunAgentInput.messages` before send; construct it in `frontend/src/runtime/AgUiRuntimeProvider.tsx`
- [ ] T024 [US2] Add a focused unit/integration assert that a 12-turn transcript results in a run payload of length 10 in `frontend/tests/trimming-http-agent.test.ts` (mock fetch); keep full messages visible in UI state

**Checkpoint**: US1 + US2 — multi-turn single thread with N=10 context window

---

## Phase 5: User Story 3 - Verify service readiness (Priority: P3)

**Goal**: Operators can check process-listening health via AG-UI `GET /status` without LLM credential checks

**Independent Test**: `make health` succeeds with backend up (even without `AI_GATEWAY_API_KEY`); fails when backend stopped (quickstart Scenario 1)

### Implementation for User Story 3

- [ ] T025 [US3] Assert in code comments + contract alignment that Agno `AGUI` exposes `GET /status` without LLM checks in `backend/agent_os.py` (reference `specs/001-agent-chat-app/contracts/ag-ui-v1.md`)
- [ ] T026 [P] [US3] Add integration test that `GET /status` returns 2xx when app is listening in `backend/tests/integration/test_status.py`
- [ ] T027 [US3] Add integration test case that `GET /status` still returns 2xx when `AI_GATEWAY_API_KEY` is unset/invalid while the process listens in `backend/tests/integration/test_status.py`
- [ ] T028 [US3] Document operator usage of existing `make health` (from T004) in root `README.md` health section (no duplicate Makefile target)

**Checkpoint**: All three user stories independently verifiable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, command surface, and quickstart validation across stories

- [ ] T029 [P] Update root `README.md` with setup (Vercel AI Gateway env: `AI_GATEWAY_API_KEY`, `LLM_MODEL_ID`, optional `AI_GATEWAY_BASE_URL`), **`VITE_AGUI_URL` only**, Makefile command index, and CORS origins
- [ ] T030 [P] Align `make test` / `make lint` with backend pytest and frontend vitest/eslint in `Makefile`
- [ ] T031 Run `specs/001-agent-chat-app/quickstart.md` scenarios 1–8 including SC-001 stopwatch check and SC-007 language rubric; record gaps as follow-ups
- [ ] T032 Confirm no login/DB/RAG/tools/attachments/prod-deploy artifacts were introduced (covers FR-008, FR-009, FR-010)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational; prefer P1 → P2 → P3
- **Polish (Phase 6)**: Depends on desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependency on US2/US3 — **MVP**
- **US2 (P2)**: After US1 provider exists; independently testable via `TrimmingHttpAgent` tests
- **US3 (P3)**: After Foundational; can proceed in parallel with US1/US2 (backend health only)

### Within Each User Story

- Pure helpers before `TrimmingHttpAgent` (US2)
- Provider before Thread mount (US1)
- Status tests before README health docs (US3)

### Parallel Opportunities

- T003, T004, T005, T006 in Setup
- T011, T012 in Foundational (frontend) while T007–T010 proceed on backend
- T015 parallel with T014
- T021 || T022 within US2
- T026 || T027 within US3
- After Foundational: US3 can run parallel to US1; US2 after US1 provider exists

---

## Parallel Example: User Story 1

```bash
# After Foundational:
Task: "T014 Configure chat agent TC instructions in backend/agent_os.py"
Task: "T015 Create Thread without stop/cancel in frontend/src/components/assistant-ui/thread.tsx"
# Then:
Task: "T016 AgUiRuntimeProvider"
Task: "T017 Mount in App.tsx"
Task: "T018–T020 validation, send gate, errors"
```

---

## Parallel Example: User Story 2

```bash
Task: "T021 sliceLastNTurns in frontend/src/runtime/trim-context.ts"
Task: "T022 unit tests in frontend/tests/trim-context.test.ts"
# Then:
Task: "T023 TrimmingHttpAgent + wire in AgUiRuntimeProvider"
Task: "T024 trimming-http-agent.test.ts payload length assert"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational
3. Complete Phase 3 US1
4. **STOP and VALIDATE** quickstart Scenario 2 (including SC-001 timing)
5. Demo local streaming chat

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → streaming MVP
3. US2 → `TrimmingHttpAgent` + N=10
4. US3 → `/status` tests + `make health` docs
5. Polish → README + full quickstart pass

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then:
   - Dev A: US1
   - Dev B: US3 (health)
   - Dev A continues US2 after US1
3. Polish together

---

## Notes

- Protocol is **AG-UI only** (`POST /agui`, `GET /status`) — do not add custom SSE adapters or `/agents/{id}/runs` clients
- Context window **N = 10** via `TrimmingHttpAgent` + `trim-context.ts` only
- Env: **`VITE_AGUI_URL` only** — no `VITE_AGENTOS_URL`
- CORS: `http://localhost:5173` and `http://127.0.0.1:5173`
- No stop/cancel control (FR-014); no DB (FR-009); no RAG/tools/uploads/prod (FR-010); credentials via env only (FR-011)
- Commit after each task or logical group
- Stop at checkpoints to validate stories independently
