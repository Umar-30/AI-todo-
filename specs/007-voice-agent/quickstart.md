# Quickstart: Voice Agent

**Feature**: 007-voice-agent
**Date**: 2026-01-23

## Overview

Add voice input/output capability to the Todo AI Chatbot. Users speak commands, the system transcribes, processes via existing AI agent, and returns spoken responses.

## Prerequisites

- Backend running with existing chat endpoint functional
- OpenRouter API key configured (for STT/TTS via OpenAI-compatible API)
- Python 3.11+

## Setup

### 1. Install Additional Dependency

```bash
cd backend
pip install python-multipart>=0.0.6
```

Or add to `requirements.txt`:
```
python-multipart>=0.0.6
```

### 2. Verify Environment

Existing `.env` should already have:
```
OPENROUTE_API_KEY=sk-or-...  # Used for STT/TTS APIs
```

No new environment variables required.

## Usage

### Endpoint

```
POST /api/{user_id}/voice-agent
Content-Type: multipart/form-data
```

### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audio` | file | Yes | Audio file (WebM, WAV, MP3, M4A) |
| `conversation_id` | string | No | UUID to continue existing conversation |

### Response

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "assistant_audio": "base64_encoded_mp3_data...",
  "transcript": "add buy groceries",
  "response_text": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"user_id": "user123", "title": "buy groceries"},
      "result": {"task_id": "...", "status": "created"}
    }
  ],
  "error": null
}
```

## Example: cURL

### New Conversation

```bash
curl -X POST "http://localhost:8000/api/user123/voice-agent" \
  -F "audio=@recording.webm"
```

### Continue Conversation

```bash
curl -X POST "http://localhost:8000/api/user123/voice-agent" \
  -F "audio=@recording.webm" \
  -F "conversation_id=550e8400-e29b-41d4-a716-446655440000"
```

## Example: JavaScript (Browser)

```javascript
// Record audio using MediaRecorder
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
const chunks = [];

recorder.ondataavailable = (e) => chunks.push(e.data);
recorder.onstop = async () => {
  const audioBlob = new Blob(chunks, { type: 'audio/webm' });

  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  // Optional: formData.append('conversation_id', conversationId);

  const response = await fetch('/api/user123/voice-agent', {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  // Play audio response
  const audioBytes = atob(data.assistant_audio);
  const audioArray = new Uint8Array(audioBytes.length);
  for (let i = 0; i < audioBytes.length; i++) {
    audioArray[i] = audioBytes.charCodeAt(i);
  }
  const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
};

// Start recording
recorder.start();
// Stop after 5 seconds (or on button click)
setTimeout(() => recorder.stop(), 5000);
```

## Error Handling

| HTTP Status | Error Code | Meaning |
|-------------|------------|---------|
| 200 | `TRANSCRIPTION_FAILED` | Audio received but couldn't be transcribed (audio response included) |
| 200 | `TTS_FAILED` | Agent responded but audio couldn't be generated |
| 400 | - | Invalid audio format |
| 403 | - | Conversation belongs to different user |
| 404 | - | Conversation not found |
| 413 | - | Audio file exceeds 25MB |
| 503 | - | Voice service unavailable |

## Architecture

```
User speaks → [Browser/App]
                    ↓
              [Voice Endpoint]
                    ↓
              [STT: Whisper]
                    ↓
              [TaskAgent] ←→ [MCP Tools] ←→ [Database]
                    ↓
              [TTS: OpenAI]
                    ↓
              [Audio Response]
                    ↓
User hears ← [Browser/App]
```

## Testing

### Manual Test

1. Start backend: `cd backend && uvicorn src.main:app --reload`
2. Record audio saying "add buy milk"
3. Send to endpoint: `curl -X POST ... -F "audio=@test.webm"`
4. Verify response contains:
   - `transcript`: "add buy milk" (or similar)
   - `tool_calls`: includes `add_task`
   - `assistant_audio`: non-empty base64 string

### Integration Test Checklist

- [ ] New conversation creates new conversation_id
- [ ] Existing conversation_id maintains context
- [ ] Invalid audio format returns 400
- [ ] Large audio (>25MB) returns 413
- [ ] Invalid conversation_id returns 404
- [ ] Transcription failure returns helpful audio error
- [ ] All task operations work (add, list, complete, delete, update)
