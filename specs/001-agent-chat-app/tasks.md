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
- [ ] T002 Initialize Python project with `agno[os,agui]` and `openai` in `backend/pyproject.toml`
- [ ] T003 [P] Initialize Vite + React + TypeScript app with `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, and `@ag-ui/client` in `frontend/package.json`
- [ ] T004 [P] Add root `Makefile` with targets `dev-backend`, `dev-frontend`, `dev`, `test`, `lint`, `health`
- [ ] T005 [P] Add `backend/.env.example` with `OPENAI_API_KEY`, `OPENAI_MODEL`, `AGENT_OS_HOST`, `AGENT_OS_PORT` and `frontend/.env.example` with `VITE_AGUI_URL`
- [ ] T006 [P] Add `.gitignore` entries for `backend/.env`, `frontend/.env.local`, `node_modules/`, `__pycache__/`, `.venv/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared config, AgentOS+AGUI shell, CORS, frontend shell, env wiring — must complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Implement env settings loader in `backend/config.py` (read `OPENAI_API_KEY`, `OPENAI_MODEL`, `AGENT_OS_HOST`, `AGENT_OS_PORT`; no import-time side effects)
- [ ] T008 Create AgentOS app with chat agent and `AGUI` interface (no `db`) in `backend/agent_os.py`
- [ ] T009 Enable CORS for local frontend origin on the AgentOS FastAPI app in `backend/agent_os.py`
- [ ] T010 Add structured JSON logging helper for AG-UI run correlation (`thread_id`, `run_id`) in `backend/agent_os.py`
- [ ] T011 [P] Implement `VITE_AGUI_URL` reader in `frontend/src/lib/env.ts`
- [ ] T012 [P] Create Vite entry and root shell in `frontend/src/main.tsx` and `frontend/src/App.tsx`
- [ ] T013 Wire `Makefile` `dev-backend` / `dev-frontend` / `health` to AgentOS serve and `curl -sf` against `/status`

**Checkpoint**: Backend serves AgentOS+AGUI; frontend boots; env URLs configurable — story work can begin

---

## Phase 3: User Story 1 - Send a message and see a streaming reply (Priority: P1) 🎯 MVP

**Goal**: User opens web chat, sends Traditional Chinese text, sees AG-UI streamed assistant reply in one thread

**Independent Test**: Open UI, send one TC message, confirm incremental assistant text without page reload (quickstart Scenario 2)

### Implementation for User Story 1

- [ ] T014 [US1] Configure chat agent Traditional Chinese reply instructions and OpenAI model from env in `backend/agent_os.py`
- [ ] T015 [P] [US1] Create assistant-ui `Thread` component without stop/cancel controls in `frontend/src/components/assistant-ui/thread.tsx`
- [ ] T016 [US1] Implement `HttpAgent` + `useAgUiRuntime` provider (single thread, `showThinking: false`) in `frontend/src/runtime/AgUiRuntimeProvider.tsx`
- [ ] T017 [US1] Mount `AgUiRuntimeProvider` and `Thread` in `frontend/src/App.tsx` using `VITE_AGUI_URL` from `frontend/src/lib/env.ts`
- [ ] T018 [US1] Reject empty/whitespace-only sends before AG-UI run (no new turn, no `/agui` call) in `frontend/src/runtime/AgUiRuntimeProvider.tsx` or `frontend/src/components/assistant-ui/thread.tsx`
- [ ] T019 [US1] Ensure send is disabled while `isRunning` and no cancel/stop UI is exposed (FR-014) in `frontend/src/components/assistant-ui/thread.tsx`
- [ ] T020 [US1] Surface stream/LLM errors on the assistant turn and allow a subsequent send after idle in `frontend/src/runtime/AgUiRuntimeProvider.tsx`

**Checkpoint**: US1 MVP — one-shot TC chat with streaming AG-UI reply works end-to-end

---

## Phase 4: User Story 2 - Continue the same thread (Priority: P2)

**Goal**: Multi-turn chat in the same page session; agent receives only last N=10 turns while UI keeps full transcript

**Independent Test**: Two sequential exchanges without leaving page; follow-up uses recent context; older-than-N turns stay visible (quickstart Scenario 3)

### Implementation for User Story 2

- [ ] T021 [P] [US2] Implement `sliceLastNTurns(messages, 10)` pure helper in `frontend/src/runtime/trim-context.ts`
- [ ] T022 [P] [US2] Add unit tests for `sliceLastNTurns` (empty, &lt;N, exactly N, &gt;N) in `frontend/tests/trim-context.test.ts`
- [ ] T023 [US2] Apply last-10 trim to AG-UI `RunAgentInput.messages` before each run while keeping full thread visible in UI in `frontend/src/runtime/AgUiRuntimeProvider.tsx`
- [ ] T024 [US2] Verify sequential turns append in one thread with send gated by `isRunning` across follow-ups in `frontend/src/components/assistant-ui/thread.tsx`

**Checkpoint**: US1 + US2 — multi-turn single thread with N=10 context window

---

## Phase 5: User Story 3 - Verify service readiness (Priority: P3)

**Goal**: Operators can check process-listening health via AG-UI `GET /status` without LLM credential checks

**Independent Test**: `make health` succeeds with backend up (even without `OPENAI_API_KEY`); fails when backend stopped (quickstart Scenario 1)

### Implementation for User Story 3

- [ ] T025 [US3] Confirm Agno `AGUI` mounts `GET /status` and document response expectation in `backend/agent_os.py` comments aligned with `specs/001-agent-chat-app/contracts/ag-ui-v1.md`
- [ ] T026 [P] [US3] Add integration test that `GET /status` returns 2xx when app is listening in `backend/tests/integration/test_status.py`
- [ ] T027 [US3] Ensure `make health` curls `{AGENTOS_BASE}/status` and exits non-zero when unreachable in `Makefile`
- [ ] T028 [US3] Verify health remains 2xx with missing/invalid `OPENAI_API_KEY` while process listens (manual or test note) in `backend/tests/integration/test_status.py`

**Checkpoint**: All three user stories independently verifiable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, command surface, and quickstart validation across stories

- [ ] T029 [P] Update root `README.md` with setup, env vars, and Makefile command index
- [ ] T030 [P] Align `make test` / `make lint` with backend pytest and frontend vitest/eslint in `Makefile`
- [ ] T031 Run `specs/001-agent-chat-app/quickstart.md` scenarios 1–8 and record any gaps as follow-ups
- [ ] T032 Confirm no login/DB/RAG/tools/attachments/prod-deploy artifacts were introduced (scope audit)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational; prefer P1 → P2 → P3
- **Polish (Phase 6)**: Depends on desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependency on US2/US3 — **MVP**
- **US2 (P2)**: After Foundational; builds on US1 chat UI but independently testable via trim + multi-turn
- **US3 (P3)**: After Foundational; can proceed in parallel with US1/US2 (backend health only)

### Within Each User Story

- Pure helpers before wiring (US2 trim)
- Provider before Thread mount (US1)
- Health contract confirmation before Makefile/test polish (US3)

### Parallel Opportunities

- T003, T004, T005, T006 in Setup
- T011, T012 in Foundational (frontend) while T007–T010 proceed on backend
- T015 parallel with T014
- T021 || T022 within US2
- T026 parallel with T025 within US3
- After Foundational: US3 can run parallel to US1; US2 after US1 provider exists

---

## Parallel Example: User Story 1

```bash
# After Foundational:
# Backend agent language/model config:
Task: "T014 Configure chat agent TC instructions in backend/agent_os.py"

# Frontend UI shell in parallel:
Task: "T015 Create Thread without stop/cancel in frontend/src/components/assistant-ui/thread.tsx"

# Then sequential wiring:
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
Task: "T023 wire trim into AgUiRuntimeProvider"
Task: "T024 multi-turn send gate verification"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational
3. Complete Phase 3 US1
4. **STOP and VALIDATE** quickstart Scenario 2
5. Demo local streaming chat

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → streaming MVP
3. US2 → multi-turn + N=10 trim
4. US3 → `/status` health + `make health`
5. Polish → README + quickstart pass

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
- Context window **N = 10** is fixed in `frontend/src/runtime/trim-context.ts`
- No stop/cancel control (FR-014); no DB (FR-009); credentials via env only (FR-011)
- Commit after each task or logical group
- Stop at checkpoints to validate stories independently
