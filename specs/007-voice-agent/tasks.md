# Tasks: Voice-Based AI Agent

**Input**: Design documents from `/specs/007-voice-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/voice-agent.yaml

**Tests**: Not explicitly requested in spec - omitting test tasks.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in descriptions

## Path Conventions

- **Web app (backend)**: `backend/src/`, `backend/tests/`
- Per plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependency for multipart form data handling

- [x] T001 Add python-multipart>=0.0.6 to backend/requirements.txt
- [x] T002 Create services directory if not exists at backend/src/services/
- [x] T003 [P] Create backend/src/services/__init__.py module file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core VoiceService that ALL user stories depend on

**⚠️ CRITICAL**: User stories cannot begin until VoiceService is complete

- [x] T004 Add VoiceError schema to backend/src/api/schemas.py
- [x] T005 Add TranscriptionResult dataclass to backend/src/services/voice_service.py
- [x] T006 Implement VoiceService.transcribe() method using OpenAI Whisper API in backend/src/services/voice_service.py
- [x] T007 Implement VoiceService.synthesize() method using OpenAI TTS API in backend/src/services/voice_service.py
- [x] T008 Add VoiceService initialization with OpenAI client in backend/src/services/voice_service.py
- [x] T009 Export VoiceService from backend/src/services/__init__.py

**Checkpoint**: VoiceService ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Voice Input with Voice Response (Priority: P1) 🎯 MVP

**Goal**: User speaks to agent, receives spoken response with task actions via MCP tools

**Independent Test**: Speak "add buy groceries", verify transcription → agent → add_task MCP call → audio response

### Implementation for User Story 1

- [x] T010 [P] [US1] Add VoiceResponse schema to backend/src/api/schemas.py
- [x] T011 [P] [US1] Add ALLOWED_AUDIO_TYPES constant to backend/src/api/voice.py
- [x] T012 [US1] Create voice router with POST /api/{user_id}/voice-agent in backend/src/api/voice.py
- [x] T013 [US1] Implement audio file validation (format, size <25MB) in backend/src/api/voice.py
- [x] T014 [US1] Implement STT call using VoiceService.transcribe() in backend/src/api/voice.py
- [x] T015 [US1] Integrate with existing TaskAgent.run() for agent processing in backend/src/api/voice.py
- [x] T016 [US1] Implement TTS call using VoiceService.synthesize() in backend/src/api/voice.py
- [x] T017 [US1] Build VoiceResponse with base64-encoded audio in backend/src/api/voice.py
- [x] T018 [US1] Register voice_router in backend/src/main.py
- [x] T019 [US1] Export voice_router from backend/src/api/__init__.py

**Checkpoint**: User Story 1 complete - voice input/output with MCP tools working ✅

---

## Phase 4: User Story 2 - Continue Voice Conversation (Priority: P1)

**Goal**: User continues conversation using conversation_id, agent maintains context

**Independent Test**: Start voice conversation, get conversation_id, send follow-up, verify context maintained

### Implementation for User Story 2

- [x] T020 [US2] Add conversation_id form field parsing to voice endpoint in backend/src/api/voice.py
- [x] T021 [US2] Implement conversation loading using existing get_conversation_with_messages in backend/src/api/voice.py
- [x] T022 [US2] Implement new conversation creation using existing create_conversation in backend/src/api/voice.py
- [x] T023 [US2] Store user message (transcribed text) using create_message in backend/src/api/voice.py
- [x] T024 [US2] Store assistant message (response text) using create_message in backend/src/api/voice.py
- [x] T025 [US2] Pass conversation history to TaskAgent.run() context in backend/src/api/voice.py
- [x] T026 [US2] Handle ConversationNotFoundError with 404 response in backend/src/api/voice.py
- [x] T027 [US2] Handle ConversationAccessDeniedError with 403 response in backend/src/api/voice.py

**Checkpoint**: User Story 2 complete - voice conversations maintain context ✅

---

## Phase 5: User Story 3 - Receive Tool Call Information (Priority: P2)

**Goal**: Response includes tool_calls array showing MCP tools invoked

**Independent Test**: Speak "add groceries", verify response contains tool_calls with add_task entry

### Implementation for User Story 3

- [x] T028 [US3] Extract tool_calls from TaskAgent result in backend/src/api/voice.py
- [x] T029 [US3] Map tool_calls to ToolCallInfo schema in backend/src/api/voice.py
- [x] T030 [US3] Include tool_calls array in VoiceResponse in backend/src/api/voice.py

**Checkpoint**: User Story 3 complete - tool calls reported in response ✅

---

## Phase 6: User Story 4 - Handle Speech Recognition Errors Gracefully (Priority: P2)

**Goal**: Transcription failures return helpful spoken error asking user to repeat

**Independent Test**: Submit noisy/unintelligible audio, verify spoken error response

### Implementation for User Story 4

- [x] T031 [US4] Define error audio messages (constants) in backend/src/api/voice.py
- [x] T032 [US4] Implement transcription failure detection in backend/src/api/voice.py
- [x] T033 [US4] Generate spoken error audio using VoiceService.synthesize() in backend/src/api/voice.py
- [x] T034 [US4] Return VoiceResponse with error field and audio for transcription failures in backend/src/api/voice.py
- [x] T035 [US4] Handle TTS failures gracefully (return text-only with error flag) in backend/src/api/voice.py
- [x] T036 [US4] Add audio format validation error (400) with supported formats in backend/src/api/voice.py
- [x] T037 [US4] Add audio size validation error (413) in backend/src/api/voice.py

**Checkpoint**: User Story 4 complete - graceful error handling with spoken feedback ✅

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation

- [x] T038 [P] Add logging for voice endpoint operations in backend/src/api/voice.py
- [x] T039 [P] Add logging for VoiceService operations in backend/src/services/voice_service.py
- [x] T040 Verify CORS configuration allows voice endpoint in backend/src/main.py
- [ ] T041 Run quickstart.md validation with cURL test commands
- [ ] T042 Manual end-to-end test with recorded audio file

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately ✅
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories ✅
- **User Story 1 (Phase 3)**: Depends on Foundational completion ✅
- **User Story 2 (Phase 4)**: Depends on User Story 1 (uses same endpoint) ✅
- **User Story 3 (Phase 5)**: Depends on User Story 1 (extends response) ✅
- **User Story 4 (Phase 6)**: Depends on Foundational (uses VoiceService) ✅
- **Polish (Phase 7)**: Depends on all user stories ✅

### User Story Dependencies

| Story | Can Start After | Dependencies | Status |
|-------|-----------------|--------------|--------|
| US1 (P1) | Foundational | VoiceService | ✅ Complete |
| US2 (P1) | US1 complete | Voice endpoint exists | ✅ Complete |
| US3 (P2) | US1 complete | Voice endpoint exists | ✅ Complete |
| US4 (P2) | Foundational | VoiceService only | ✅ Complete |

### Within Each User Story

- Schemas before endpoint implementation
- Validation before processing logic
- Core flow before error handling

### Parallel Opportunities

- T002, T003 can run in parallel (Setup) ✅
- T010, T011 can run in parallel (US1 schemas/constants) ✅
- T038, T039 can run in parallel (Logging) ✅
- US3 and US4 can run in parallel (both only need US1 complete or Foundational) ✅

---

## Summary

| Phase | Tasks | Description | Status |
|-------|-------|-------------|--------|
| Setup | T001-T003 (3) | Dependencies, directory structure | ✅ Complete |
| Foundational | T004-T009 (6) | VoiceService (STT/TTS) | ✅ Complete |
| US1 (P1) | T010-T019 (10) | Core voice flow - MVP | ✅ Complete |
| US2 (P1) | T020-T027 (8) | Conversation continuity | ✅ Complete |
| US3 (P2) | T028-T030 (3) | Tool call reporting | ✅ Complete |
| US4 (P2) | T031-T037 (7) | Error handling | ✅ Complete |
| Polish | T038-T042 (5) | Logging, validation | 🔄 In Progress (3/5) |

**Total**: 42 tasks | **Completed**: 40 | **Remaining**: 2 (manual testing)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story independently testable after completion
- No database changes required (reuses existing models)
- VoiceService is the only new service component
- Voice endpoint mirrors chat endpoint pattern
