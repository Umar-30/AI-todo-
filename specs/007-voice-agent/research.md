# Research: Voice Agent Implementation

**Feature**: 007-voice-agent
**Date**: 2026-01-23

## Research Questions

### 1. STT (Speech-to-Text) Service Selection

**Question**: Which speech-to-text service should be used for transcribing user audio?

**Decision**: OpenAI Whisper API via OpenRouter

**Rationale**:
- OpenRouter already integrated in the codebase for LLM access
- Whisper provides industry-leading transcription accuracy (95%+)
- Supports multiple audio formats (WAV, MP3, WebM, FLAC, M4A)
- Stateless API call fits existing architecture pattern
- Cost-effective and well-documented

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Google Speech-to-Text | High accuracy, streaming | Requires separate GCP setup, additional credentials | Added complexity, separate auth |
| Azure Cognitive Services | Enterprise features | Requires Azure account, different SDK | Over-engineering for current needs |
| Local Whisper (whisper.cpp) | No API cost, offline | Requires GPU/CPU resources, deployment complexity | Stateless design conflict |
| Deepgram | Real-time, websockets | Additional vendor, streaming adds complexity | Not needed for request-response model |

---

### 2. TTS (Text-to-Speech) Service Selection

**Question**: Which text-to-speech service should be used for generating audio responses?

**Decision**: OpenAI TTS API via OpenRouter (or direct OpenAI API)

**Rationale**:
- Consistent with STT choice (same vendor)
- Natural-sounding voices (alloy, echo, fable, onyx, nova, shimmer)
- Simple API: text in, audio out
- Supports MP3, opus, aac, flac output formats
- Stateless design compatible

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|------------|------|------|------------------|
| Google Cloud TTS | Many voices, SSML support | Separate GCP setup | Added complexity |
| Amazon Polly | Neural voices | AWS account required | Different auth system |
| ElevenLabs | Most natural voices | Premium pricing, separate vendor | Cost, complexity |
| gTTS (local) | Free, no API | Low quality, robotic | Poor user experience |

---

### 3. Audio Format Handling

**Question**: What audio formats should be accepted/returned?

**Decision**:
- **Input**: Accept WebM (browser default), WAV, MP3, M4A
- **Output**: Return MP3 (universal playback support)

**Rationale**:
- WebM is default for browser MediaRecorder API
- MP3 has universal playback support across all devices
- FastAPI can handle multipart/form-data for audio upload
- Response can be streamed or base64-encoded

---

### 4. Request/Response Architecture

**Question**: How should audio be transmitted in API requests/responses?

**Decision**:
- **Request**: `multipart/form-data` with audio file + JSON metadata
- **Response**: JSON with base64-encoded audio or streaming audio

**Rationale**:
- Multipart form-data is standard for file uploads
- Base64 encoding simplifies JSON response parsing
- Optional streaming for lower latency (future enhancement)

**Implementation Pattern**:
```
Request:
POST /api/{user_id}/voice-agent
Content-Type: multipart/form-data
- audio: binary file
- conversation_id: optional UUID (form field)

Response:
{
  "conversation_id": "uuid",
  "assistant_audio": "base64_encoded_mp3",
  "transcript": "what user said",
  "response_text": "what agent replied",
  "tool_calls": [...]
}
```

---

### 5. Error Handling Strategy

**Question**: How should transcription failures be handled?

**Decision**: Return spoken error response with fallback text

**Rationale**:
- Voice-first experience means errors should also be spoken
- Fallback text ensures accessibility
- Low-confidence transcriptions trigger clarification request

**Error Response Pattern**:
```json
{
  "conversation_id": "uuid",
  "assistant_audio": "base64_encoded_error_message",
  "transcript": null,
  "response_text": "I couldn't understand that. Could you please repeat?",
  "tool_calls": [],
  "error": {
    "code": "TRANSCRIPTION_FAILED",
    "message": "Speech could not be transcribed"
  }
}
```

---

### 6. Latency Optimization

**Question**: How to meet the 8-second response time target?

**Decision**: Sequential processing with async I/O

**Rationale**:
- STT + Agent + TTS must complete within 8 seconds
- Expected breakdown:
  - STT: ~1-2 seconds
  - Agent processing: ~2-3 seconds (existing chat endpoint)
  - TTS: ~1-2 seconds
  - Network overhead: ~1-2 seconds
- Async I/O ensures no blocking during API calls

**Optimization Options** (if needed later):
- Stream TTS audio while generating (reduces perceived latency)
- Cache common TTS responses (greetings, error messages)
- Use faster models for simple queries

---

## Dependencies Verified

| Dependency | Status | Notes |
|-----------|--------|-------|
| OpenAI Python SDK | Already installed | Used by task_agent.py |
| FastAPI multipart | Available | Built into FastAPI |
| python-multipart | May need to add | For form data parsing |
| 005-chat-endpoint | Complete | Conversation management reusable |
| 004-ai-intent-agent | Complete | TaskAgent class reusable |
| 003-mcp-task-tools | Complete | MCP tools operational |

---

## New Dependencies Required

```
# Add to requirements.txt
python-multipart>=0.0.6  # For multipart/form-data parsing
```

---

## Constitution Compliance Check

| Principle | Compliant | Notes |
|-----------|-----------|-------|
| I. MCP-Compliant Architecture | ✅ | Voice layer wraps existing MCP tools |
| II. Database as Single Source of Truth | ✅ | Conversation storage unchanged |
| III. Stateless Agent Design | ✅ | No voice-specific state maintained |
| IV. Tool-Driven Operations | ✅ | All task ops via MCP tools |
| V. AI Behavior Constraints | ✅ | Agent receives text only |
| VI. Security and Authentication | ✅ | user_id passed through |

---

## Summary

The voice agent will:
1. Accept audio via multipart/form-data POST
2. Transcribe using OpenAI Whisper API
3. Pass text to existing TaskAgent (unchanged)
4. Convert response text to audio via OpenAI TTS API
5. Return JSON with base64 audio + metadata

No changes to existing agent, MCP tools, or database layer required.
