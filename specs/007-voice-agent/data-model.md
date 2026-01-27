# Data Model: Voice Agent

**Feature**: 007-voice-agent
**Date**: 2026-01-23

## Overview

The voice agent introduces no new database entities. It operates as a stateless voice layer that:
1. Converts speech to text
2. Delegates to existing chat/agent infrastructure
3. Converts response text to speech

All conversation and message persistence uses existing models from 005-chat-endpoint.

---

## Existing Entities (Reused)

### Conversation
From `backend/src/models/conversation.py`:
- `id`: UUID (primary key)
- `user_id`: str (owner)
- `created_at`: datetime
- `updated_at`: datetime

**Voice Agent Usage**: Same as text chat - creates/continues conversations.

### Message
From `backend/src/models/message.py`:
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key)
- `user_id`: str
- `role`: str ("user" | "assistant")
- `content`: str (text only - transcribed for voice input)
- `created_at`: datetime

**Voice Agent Usage**: Stores transcribed user speech and agent text response.

---

## New Request/Response Schemas

### VoiceRequest (API Input)

```python
class VoiceRequest:
    """
    Multipart form data for voice input.

    Fields:
        audio: UploadFile - Audio file (WebM, WAV, MP3, M4A)
        conversation_id: Optional[UUID] - Existing conversation to continue
    """
    audio: UploadFile  # Required, max 25MB
    conversation_id: Optional[UUID] = None
```

**Validation Rules**:
- `audio`: Required, must be valid audio file
- `audio.content_type`: Must be in ["audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/x-m4a"]
- `audio.size`: Max 25MB (Whisper API limit)
- `conversation_id`: If provided, must exist and belong to user_id

---

### VoiceResponse (API Output)

```python
class VoiceResponse:
    """
    Response from voice agent endpoint.

    Fields:
        conversation_id: UUID - Conversation identifier
        assistant_audio: str - Base64-encoded MP3 audio
        transcript: Optional[str] - What user said (null on transcription failure)
        response_text: str - Agent's text response
        tool_calls: List[ToolCallInfo] - MCP tools invoked
        error: Optional[VoiceError] - Error details if failed
    """
    conversation_id: UUID
    assistant_audio: str  # Base64-encoded MP3
    transcript: Optional[str] = None
    response_text: str
    tool_calls: List[ToolCallInfo] = []
    error: Optional[VoiceError] = None
```

---

### VoiceError (Error Schema)

```python
class VoiceError:
    """
    Error information for voice processing failures.

    Fields:
        code: str - Error code for client handling
        message: str - Human-readable error message
    """
    code: str  # e.g., "TRANSCRIPTION_FAILED", "TTS_FAILED", "AUDIO_INVALID"
    message: str
```

**Error Codes**:
| Code | Description |
|------|-------------|
| `TRANSCRIPTION_FAILED` | Could not transcribe audio |
| `TTS_FAILED` | Could not generate audio response |
| `AUDIO_INVALID` | Invalid audio format or corrupted file |
| `AUDIO_TOO_LARGE` | Audio exceeds 25MB limit |
| `AUDIO_TOO_SHORT` | Audio too short to contain speech |

---

## Service Layer (New Components)

### VoiceService

```python
class VoiceService:
    """
    Handles STT and TTS operations.

    Stateless - each method is a pure function with API calls.
    """

    async def transcribe(self, audio: bytes, content_type: str) -> TranscriptionResult:
        """
        Convert audio to text using Whisper API.

        Args:
            audio: Raw audio bytes
            content_type: MIME type of audio

        Returns:
            TranscriptionResult with text or error
        """
        pass

    async def synthesize(self, text: str, voice: str = "alloy") -> bytes:
        """
        Convert text to audio using TTS API.

        Args:
            text: Text to speak
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            MP3 audio bytes
        """
        pass
```

### TranscriptionResult

```python
class TranscriptionResult:
    """
    Result of speech-to-text operation.

    Fields:
        text: Optional[str] - Transcribed text (null on failure)
        confidence: Optional[float] - Confidence score (0-1)
        error: Optional[str] - Error message if failed
    """
    text: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.text is not None and self.error is None
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Voice Agent Endpoint                         │
│                   POST /api/{user_id}/voice-agent                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  1. Receive audio (multipart/form-data)                             │
│     - Validate format and size                                      │
│     - Extract conversation_id if provided                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. Speech-to-Text (VoiceService.transcribe)                        │
│     - Call Whisper API                                              │
│     - Return transcript or error                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                   [Success]               [Failure]
                        │                       │
                        ▼                       ▼
┌───────────────────────────────┐   ┌──────────────────────────────┐
│  3. Process with TaskAgent    │   │  Generate error audio        │
│     - Load conversation       │   │  "I couldn't understand..."  │
│     - Run agent (MCP tools)   │   │  Return error response       │
│     - Store messages in DB    │   └──────────────────────────────┘
└───────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. Text-to-Speech (VoiceService.synthesize)                        │
│     - Convert agent response to audio                               │
│     - Return MP3 bytes                                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. Return VoiceResponse                                            │
│     - Base64-encode audio                                           │
│     - Include transcript, response_text, tool_calls                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Placement

```
backend/src/
├── api/
│   ├── voice.py          # NEW: Voice endpoint router
│   └── schemas.py        # MODIFY: Add VoiceRequest, VoiceResponse, VoiceError
├── services/
│   └── voice_service.py  # NEW: STT/TTS service
└── main.py               # MODIFY: Register voice router
```

---

## No Database Changes Required

The voice agent:
- Uses existing Conversation and Message tables
- Stores transcribed text (not audio) in messages
- Maintains same stateless, MCP-only architecture

Audio is transient - processed and returned, never stored.
