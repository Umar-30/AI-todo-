"""
Voice Agent API endpoint for Todo AI Chatbot.

Implements POST /api/{user_id}/voice-agent for voice-based chat interactions.
Converts speech to text, processes through AI agent, and returns synthesized audio.
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile

from .schemas import ToolCallInfo, VoiceError, VoiceResponse
from .services import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
    create_conversation,
    create_message,
    get_conversation_with_messages,
)
from ..agent import create_task_agent
from ..services import VoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Voice"])

# Allowed audio content types for voice input
ALLOWED_AUDIO_TYPES = [
    "audio/webm",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a",
    "audio/ogg",
    "audio/flac",
]

# Maximum audio file size (25MB - Whisper API limit)
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB in bytes

# Error messages for TTS
ERROR_MESSAGES = {
    "transcription_failed": "I'm sorry, I couldn't understand what you said. Could you please try again?",
    "tts_failed": "I was able to process your request, but I couldn't generate an audio response.",
    "audio_invalid": "The audio format is not supported. Please use WebM, WAV, MP3, or M4A format.",
    "audio_too_large": "The audio file is too large. Please keep recordings under 25 megabytes.",
    "audio_too_short": "The audio recording was too short. Please try speaking for a bit longer.",
}


def _get_file_extension(content_type: str) -> str:
    """Get file extension from content type."""
    type_to_ext = {
        "audio/webm": "webm",
        "audio/wav": "wav",
        "audio/wave": "wav",
        "audio/x-wav": "wav",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/mp4": "m4a",
        "audio/x-m4a": "m4a",
        "audio/m4a": "m4a",
        "audio/ogg": "ogg",
        "audio/flac": "flac",
    }
    return type_to_ext.get(content_type, "webm")


@router.post(
    "/{user_id}/voice-agent",
    response_model=VoiceResponse,
    responses={
        200: {"description": "Successful voice response"},
        400: {"description": "Bad request (invalid audio format)"},
        403: {"description": "Access denied (conversation belongs to different user)"},
        404: {"description": "Conversation not found"},
        413: {"description": "Audio file too large (max 25MB)"},
        500: {"description": "Internal server error"},
        503: {"description": "Voice service unavailable"},
    },
    summary="Process voice input",
    description="Accept audio input, transcribe, process through AI agent, and return synthesized audio response.",
)
async def voice_agent(
    user_id: str = Path(..., min_length=1, description="User's unique identifier"),
    audio: UploadFile = File(..., description="Audio file (WebM, WAV, MP3, M4A)"),
    conversation_id: Optional[str] = Form(default=None, description="Existing conversation ID to continue"),
) -> VoiceResponse:
    """
    Process voice input and return voice response.

    Accepts audio, transcribes to text, processes through AI agent,
    and returns synthesized audio response along with metadata.
    """
    logger.info(f"Voice request from user {user_id}")

    # Initialize voice service
    voice_service = VoiceService()

    # ===== T036/T037: Audio Validation =====
    # Validate audio content type
    content_type = audio.content_type or "audio/webm"
    if content_type not in ALLOWED_AUDIO_TYPES:
        logger.warning(f"Invalid audio format: {content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format: {content_type}. Supported formats: {', '.join(ALLOWED_AUDIO_TYPES)}",
        )

    # Read audio content
    audio_bytes = await audio.read()

    # Validate audio size
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        logger.warning(f"Audio too large: {len(audio_bytes)} bytes")
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large ({len(audio_bytes)} bytes). Maximum size is 25MB.",
        )

    # Validate minimum audio size (too short to contain speech)
    if len(audio_bytes) < 1000:  # Less than 1KB is likely too short
        logger.warning(f"Audio too short: {len(audio_bytes)} bytes")
        # Generate error audio response
        try:
            error_audio = await voice_service.synthesize(ERROR_MESSAGES["audio_too_short"])
            error_audio_b64 = voice_service.encode_audio_base64(error_audio)
        except Exception:
            error_audio_b64 = ""

        # Need a conversation_id for response - create one if not provided
        conv_id = UUID(conversation_id) if conversation_id else create_conversation(user_id).id

        return VoiceResponse(
            conversation_id=conv_id,
            assistant_audio=error_audio_b64,
            transcript=None,
            response_text=ERROR_MESSAGES["audio_too_short"],
            tool_calls=[],
            error=VoiceError(code="AUDIO_TOO_SHORT", message=ERROR_MESSAGES["audio_too_short"]),
        )

    # ===== T020-T027: Conversation Management =====
    # Parse conversation_id if provided
    conv_uuid: Optional[UUID] = None
    if conversation_id:
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            logger.warning(f"Invalid conversation_id format: {conversation_id}")
            raise HTTPException(
                status_code=400,
                detail="Invalid conversation_id format. Must be a valid UUID.",
            )

    # Load or create conversation
    message_history: list[dict[str, str]] = []

    try:
        if conv_uuid:
            # Continue existing conversation
            logger.info(f"Loading conversation {conv_uuid}")
            try:
                conversation, messages = get_conversation_with_messages(conv_uuid, user_id)
                conv_uuid = conversation.id

                # Build message history for agent context
                for msg in messages:
                    message_history.append({
                        "role": msg.role,
                        "content": msg.content,
                    })
                logger.info(f"Loaded {len(messages)} messages from conversation")

            except ConversationNotFoundError:
                logger.warning(f"Conversation {conv_uuid} not found")
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )
            except ConversationAccessDeniedError:
                logger.warning(f"User {user_id} denied access to conversation {conv_uuid}")
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to conversation",
                )
        else:
            # Create new conversation
            logger.info(f"Creating new conversation for user {user_id}")
            conversation = create_conversation(user_id)
            conv_uuid = conversation.id
            logger.info(f"Created conversation {conv_uuid}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation management error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to manage conversation",
        )

    # ===== T014/T032-T034: Speech-to-Text =====
    file_ext = _get_file_extension(content_type)
    transcription = await voice_service.transcribe(
        audio_bytes,
        content_type,
        filename=f"audio.{file_ext}",
    )

    # Handle transcription failure
    if not transcription.success:
        logger.warning(f"Transcription failed: {transcription.error}")

        # Generate error audio response
        try:
            error_audio = await voice_service.synthesize(ERROR_MESSAGES["transcription_failed"])
            error_audio_b64 = voice_service.encode_audio_base64(error_audio)
        except Exception as e:
            logger.error(f"Failed to generate error audio: {e}")
            error_audio_b64 = ""

        return VoiceResponse(
            conversation_id=conv_uuid,
            assistant_audio=error_audio_b64,
            transcript=None,
            response_text=ERROR_MESSAGES["transcription_failed"],
            tool_calls=[],
            error=VoiceError(
                code="TRANSCRIPTION_FAILED",
                message=transcription.error or "Speech could not be transcribed",
            ),
        )

    transcript_text = transcription.text
    logger.info(f"Transcription: '{transcript_text}'")

    # ===== T023: Store user message =====
    create_message(
        user_id=user_id,
        conversation_id=conv_uuid,
        role="user",
        content=transcript_text,
    )
    logger.info("Stored user message (transcribed)")

    # ===== T015/T025: Process with TaskAgent =====
    agent = create_task_agent()
    tool_calls: list[ToolCallInfo] = []

    try:
        # Build context with conversation history
        context = {
            "conversation_history": message_history,
        }

        # Execute agent
        agent_result = await agent.run(
            message=transcript_text,
            user_id=user_id,
            context=context,
        )

        # Extract response and tool calls
        response_text = agent_result.get("response", "")
        raw_tool_calls = agent_result.get("tool_calls", [])

        # ===== T028-T030: Map tool calls =====
        for tc in raw_tool_calls:
            tool_calls.append(ToolCallInfo(
                name=tc.get("name", "unknown"),
                arguments=tc.get("arguments", {}),
                result=tc.get("result"),
            ))

        logger.info(f"Agent response received, {len(tool_calls)} tool calls")

    except Exception as e:
        logger.error(f"Agent processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process message",
        )

    # ===== T024: Store assistant response =====
    create_message(
        user_id=user_id,
        conversation_id=conv_uuid,
        role="assistant",
        content=response_text,
    )
    logger.info("Stored assistant response")

    # ===== T016/T017/T035: Text-to-Speech =====
    error_info: Optional[VoiceError] = None

    try:
        audio_response = await voice_service.synthesize(response_text)
        audio_b64 = voice_service.encode_audio_base64(audio_response)
        logger.info(f"TTS successful: {len(audio_response)} bytes")

    except Exception as e:
        logger.error(f"TTS failed: {e}")
        # Return response without audio, with error flag
        audio_b64 = ""
        error_info = VoiceError(
            code="TTS_FAILED",
            message=ERROR_MESSAGES["tts_failed"],
        )

    return VoiceResponse(
        conversation_id=conv_uuid,
        assistant_audio=audio_b64,
        transcript=transcript_text,
        response_text=response_text,
        tool_calls=tool_calls,
        error=error_info,
    )
